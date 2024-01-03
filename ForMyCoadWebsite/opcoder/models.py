from django.db import models

# future=> photo.
 
class Blog(models.Model):
    sno = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    content = models.TextField()
    longcontent = models.TextField(default='akshat')
    slug = models.CharField(max_length=100)
    time = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.title


class Comment(models.Model):
    sno = models.AutoField(primary_key=True)
    name = models.CharField(max_length=40)
    email = models.CharField(max_length=40)
    desc = models.TextField()
    time = models.DateTimeField(auto_now_add=True)

class Video(models.Model):
    sno = models.AutoField(primary_key=True)
    pf = models.CharField(max_length=1)
    title = models.CharField(max_length=200)
    visi = models.BooleanField() # visibility
    desc = models.TextField()
    thumbnail = models.CharField(max_length=250)
    date = models.DateTimeField(auto_now_add=True)
    tviews = models.PositiveIntegerField()
    tlikes = models.PositiveIntegerField()
    slug = models.CharField(max_length=25)
    source = models.CharField(max_length=300)
    def __str__(self):
        return self.slug


class Playlist(models.Model):
    sno = models.AutoField(primary_key=True)
    pf = models.CharField(max_length=1)
    title = models.CharField(max_length=200)
    visi = models.BooleanField() # visibility
    desc = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    thumbnail = models.CharField(max_length=300)
    slug = models.CharField(max_length=25)
    def __str__(self):
        return self.slug
