from django.db import models
from django.contrib.auth.models import User
from django_ckeditor_5.fields import CKEditor5Field
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys
import requests
from .utils import generate_fixed_length_slug, img_preprocessing

from django.dispatch import receiver
from django.db.models.signals import post_save
from allauth.account.signals import user_signed_up
from allauth.socialaccount.models import SocialAccount
from django.core.files.base import ContentFile

class Subscription(models.Model):
    subscriber = models.ForeignKey(User, related_name='following', on_delete=models.CASCADE)
    profile = models.ForeignKey('Profile', related_name='followers', on_delete=models.CASCADE)
    date_subscribed = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('subscriber', 'profile')

    def __str__(self):
        return f"{self.subscriber.username} follows {self.profile.user.username}"

class Profile(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    age = models.PositiveIntegerField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    profile_photo = models.ImageField(upload_to='profile_pics/', default='profile_pics/default.jpg')
    subscribers = models.ManyToManyField(User, through=Subscription, related_name='subscriptions', blank=True)

    def __str__(self):
        return f'{self.user.username} Profile'

    def total_subscribers(self):
        return self.subscribers.count()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

@receiver(user_signed_up)
def populate_profile_google(request, user, **kwargs):
    social_account = SocialAccount.objects.filter(user=user, provider='google').first()
    if social_account:
        picture_url = social_account.extra_data.get('picture')
        if picture_url:
            try:
                response = requests.get(picture_url)
                if response.status_code == 200:
                    file_name = f"google_avatar_{user.username}.jpg"
                    user.profile.profile_photo.save(
                        file_name,
                        ContentFile(response.content),
                        save=True
                    )
            except Exception:
                pass

#  Content Models
class Blog(models.Model):
    sno = models.AutoField(primary_key=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=300)
    content = CKEditor5Field(config_name='extends')
    slug = models.CharField(max_length=100)
    time = models.DateTimeField(auto_now_add=True)
    views = models.PositiveIntegerField()
    likes = models.PositiveIntegerField()

    def __str__(self):
        return self.title


class BlogComment(models.Model):
    blog = models.ForeignKey(Blog, related_name="blogComment", on_delete=models.CASCADE)
    name = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s - %s" % (self.blog.title, self.name)


class Playlist(models.Model):
    sno = models.AutoField(primary_key=True)
    title = models.CharField(max_length=250)
    desc = models.TextField()
    thumbnail = models.ImageField(upload_to ='playlistThumbnail/')
    date = models.DateTimeField(auto_now_add=True)
    visi = models.BooleanField(default=True)  # True-visible
    slug = models.CharField(max_length=23, blank=True)

    def __str__(self):
        return "%s - %s" % (self.slug, self.title)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_fixed_length_slug(self.title)

        if self.pk and Playlist.objects.filter(pk=self.pk).exists():  # Check if updating an existing instance
            old = Playlist.objects.get(pk=self.pk)  # old = old_instance
            if old.thumbnail and old.thumbnail != self.thumbnail:
                old.thumbnail.delete(save=False)  # Delete old photo from S3
            else:
                return super().save(*args, **kwargs)

        output = img_preprocessing(self.thumbnail)
        self.thumbnail = InMemoryUploadedFile(
            output, 'ImageField', f"{self.thumbnail.name.split('.')[0]}.png",
            'image/png', sys.getsizeof(output), None)

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.thumbnail:  # Check if there is an image
            self.thumbnail.delete(save=False)

        super().delete(*args, **kwargs)  # Delete the model instance


class Video(models.Model):
    sno = models.AutoField(primary_key=True)
    title = models.CharField(max_length=250)
    playlist = models.ForeignKey(Playlist, related_name="playlist", on_delete=models.SET_NULL, null=True, blank=True)
    desc = models.TextField()
    thumbnail = models.ImageField(upload_to ='videoThumbnail/')
    date = models.DateTimeField(auto_now_add=True)
    visi = models.BooleanField(default=True)  # True-visible
    tviews = models.PositiveIntegerField(default=0)
    tlikes = models.PositiveIntegerField(default=0)
    slug = models.CharField(max_length=23, blank=True)
    source = models.CharField(max_length=200, blank=True)
    categories = models.CharField(max_length=350)

    def __str__(self):
        return "%s - %s" % (self.slug, self.title)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_fixed_length_slug(self.title)

        if self.pk and Video.objects.filter(pk=self.pk).exists():  # Check if updating an existing instance
            old = Video.objects.get(pk=self.pk)  # old = old_instance
            if old.thumbnail and old.thumbnail != self.thumbnail:
                old.thumbnail.delete(save=False)  # Delete old photo from S3
            else:
                return super().save(*args, **kwargs)

        output = img_preprocessing(self.thumbnail)
        self.thumbnail = InMemoryUploadedFile(
            output, 'ImageField', f"{self.thumbnail.name.split('.')[0]}.png",
            'image/png', sys.getsizeof(output), None)

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.thumbnail:  # Check if there is an image
            self.thumbnail.delete(save=False)

        super().delete(*args, **kwargs)  # Delete the model instance


class VideoComment(models.Model):
    video = models.ForeignKey(Video, related_name="videoComment", on_delete=models.CASCADE)
    name = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s - %s" % (self.video.title, self.name)


FEEDBACK_CATEGORIES = [
    ('BUG', 'Technical Bug Report'),
    ('FEATURE', 'Feature Request / Suggestion'),
    ('UI', 'UI/UX Improvement'),
    ('CONTENT', 'Content Quality/Correction'),
    ('GENERAL', 'General Inquiry/Praise'),
]

RATING_CHOICES = [
    (1, '1 - Very Dissatisfied'),
    (2, '2 - Dissatisfied'),
    (3, '3 - Neutral'),
    (4, '4 - Satisfied'),
    (5, '5 - Very Satisfied'),
]

class UserFeedback(models.Model):
    sno = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,)
    name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(max_length=100, null=True, blank=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    category = models.CharField(max_length=10, choices=FEEDBACK_CATEGORIES,default='GENERAL')
    rating = models.IntegerField(choices=RATING_CHOICES, default=5,
                                 help_text="User's satisfaction rating (1 to 5 stars).")
    date = models.DateTimeField(auto_now_add=True)
    admin_notes = models.TextField(blank=True, null=True, help_text="Internal notes on resolution or triage.")

    class Meta:
        verbose_name_plural = "User Feedback"
        ordering = ['-date']

    def __str__(self):
        return f"[{self.get_category_display()}] {self.subject} by {self.name or self.email or 'Anonymous'}"
