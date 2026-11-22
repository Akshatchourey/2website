from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from math import ceil as c
from .models import Profile, Subscription, UserAnalyse, Blog, BlogComment, Video
from django.db.models import F
from django.db.models.expressions import RawSQL

from re import sub
import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

import boto3
from botocore.exceptions import ClientError
from django.conf import settings

# Create your views here.

COMMON_STOP_WORDS = {
    'the', 'a', 'an', 'is', 'are', 'was', 'were', 'of', 'in', 'on', 'at',
    'to', 'for', 'with', 'and', 'but', 'or', 'by', 'as', 'it', 'its'}

def index(request):
    return render(request, "opcoder/index.html")

def search(request):
    query_string = request.GET.get('slug', '')
    blog_results = Blog.objects.none()
    video_results = Video.objects.none()

    query_string = query_string.lower()
    # Remove punctuation
    query_string = sub(r'[^\w\s]', ' ', query_string)
    words = query_string.split()
    filtered_words = [word for word in words if word not in COMMON_STOP_WORDS]

    # Adding query to UserAnalysis
    query = filtered_words
    if query and request.user.is_authenticated:
        analysis, _ = UserAnalyse.objects.get_or_create(user=request.user)
        analysis.add_search_query(query)

    # 4. Re-join the clean words into a string for the MySQL FTS engine
    # We use '+' to force MySQL to match ALL words (Boolean Mode)  or f"'{query}*'"
    search_term = " ".join(f'+{word}' for word in filtered_words)

    fts_rank_sql = "MATCH (title) AGAINST (%s IN BOOLEAN MODE)"
    if search_term:
        blog_results = Blog.objects.annotate(
            rank=RawSQL(fts_rank_sql, (search_term,))
        ).filter(rank__gt=0).order_by('-rank', '-time')

        video_results = Video.objects.annotate(
            rank=RawSQL(fts_rank_sql, (search_term,))
        ).filter(rank__gt=0).order_by('-rank', '-tviews')

    total_results = len(blog_results) + len(video_results)

    context = {'query': query_string, 'blog_results': blog_results, 'video_results': video_results, 'total_results':total_results}

    return render(request, 'opcoder/search_results.html', context)

@login_required(login_url='/login/')
@require_POST
def toggle_subscribe(request, user_id):
    target_user = get_object_or_404(User, pk=user_id)

    if request.user == target_user:
        return JsonResponse({"status": "failed", "message": "Cannot subscribe to yourself"}, status=400)

    target_profile = target_user.profile
    subscription = Subscription.objects.filter(subscriber=request.user, profile=target_profile).first()

    if subscription:
        subscription.delete()
        subscribed = False
    else:
        Subscription.objects.create(subscriber=request.user, profile=target_profile)
        subscribed = True

    return JsonResponse({
        'status': 'success',
        'subscribed': subscribed,
        'subscriber_count': target_profile.total_subscribers()
    })

def profile(request):
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME,
    )

    s3_files = {
        "project_1_1": "projectImg/project 1_1.png",
        "project_1_2": "projectImg/project 1_2.png",
        "project_1_3": "projectImg/project 1_3.png",
        "project_1_4": "projectImg/project 1_4.png",
        "project_1_5": "projectImg/project 1_5.png",
        "project_1_6": "projectImg/project 1_6.png",
        "project_2_1": "projectImg/project 2_1.png",
        "project_2_2": "projectImg/project 2_2.png",
        "project_2_3": "projectImg/project 2_3.png",
        "project_2_4": "projectImg/project 2_4.png",
        "project_2_5": "projectImg/project 2_5.png",
        "project_2_6": "projectImg/project 2_6.png",
        "project_3_1": "projectImg/project 3_1.png",
        "project_3_2": "projectImg/project 3_2.png",
        "project_3_3": "projectImg/project 3_3.png",
        "project_3_4": "projectImg/project 3_4.png",
        "project_3_5": "projectImg/project 3_5.png",
        "project_3_6": "projectImg/project 3_6.png",

        "Internship_Infotact": "certificates/Internship Infotact.png",
        "Internship_Paranabhuti": "certificates/Internship Paranubhuti Foundation.jpg",
        "NPTEL_cloud_Computing": "certificates/NPTEL Cloud Computing.png",
        "NPTEL_Marketing": "certificates/NPTEL Marketing Analytics.png",
        "AWS_Technical_Essentials": "certificates/AWS Technical Essentials.png",
        "AWS_Cloud_Practitioner": "certificates/AWS Cloud Practitioner.png",
        "Coursera_ComputerNetworking": "certificates/Coursera_ComputerNetworking.png",
        "Python_Certificate": "certificates/Python Certificate.png",
        "Intern_Hackerrank": "certificates/Software Engineer Intern Hackerrank.png",
        "java_basic_Hackerrank": "certificates/javabasic Hackerrank.png",
        "python_solving_hackerrank": "certificates/problem SolvingBasic Hackerrank.png",
        "python_basic_hackerrank": "certificates/PythonBasic Hackerrank.png",
        "AIML_Certificate": "certificates/AIML Certificate.png",
        "MathLabOnramp": "certificates/MathLabOnramp.png",
    }

    signed_urls = {}
    for key, s3_path in s3_files.items():
        try:
            url = s3_client.generate_presigned_url(
                "get_object",
                Params={
                    "Bucket": settings.AWS_STORAGE_BUCKET_NAME,
                    "Key": s3_path,
                },
                ExpiresIn=3600,  # URL expires in 1 hour (3600 seconds)
            )
            signed_urls[key] = url
        except ClientError as e:
            print(f"Error signing {s3_path}: {e}")
            signed_urls[key] = ""

    context = {
        "s3_urls": signed_urls,
    }
    return render(request, "opcoder/profile.html", context)

def show_blog(request, blogs):
    no_of_posts = 6
    page = request.GET.get('page')
    if page is None:
        page = 1
    else:
        page = int(page)

    length = len(blogs)
    blogs = blogs[(page-1)*no_of_posts: page*no_of_posts]
    if page > 1:
        prev = page-1
    else:
        prev = None
    if page < c(length/no_of_posts):
        nxt = page + 1
    else:
        nxt = None
    context = {'blogs': blogs, 'prev': prev, 'nxt': nxt}
    return render(request, 'opcoder/blogs.html', context)

def blog(request):
    blogs = Blog.objects.all().order_by('-time')
    return show_blog(request, blogs)

def blogpost(request, slug):
    this_blog = get_object_or_404(Blog, slug=slug)
    comments = this_blog.blogComment.all().order_by("-date")
    Blog.objects.filter(pk=this_blog.pk).update(views=F('views') + 1)

    owner_sub_count = this_blog.owner.profile.total_subscribers()

    user_has_liked = False
    is_subscribed = False
    if request.user.is_authenticated:
        analysis, _ = UserAnalyse.objects.get_or_create(user=request.user)

        if not analysis.viewed_blogs.filter(pk=this_blog.pk).exists():
            analysis.viewed_blogs.add(this_blog)

        if analysis.liked_blogs.filter(pk=this_blog.pk).exists():
            user_has_liked = True

        is_subscribed = Subscription.objects.filter(
            subscriber=request.user, profile=this_blog.owner.profile).exists()

        # analysis = getattr(request.user, 'analysis', None)# lazy loading for speed BCZ we just need to check,not need

    context = {'post': this_blog, 'comments':comments, 'user_has_liked': user_has_liked, 'is_subscribed': is_subscribed, 'owner_sub_count': owner_sub_count}
    return render(request, 'opcoder/blogpost.html', context)

@login_required(login_url='/login/')
@require_POST
def like_blog_post(request, pk):
    blog_post = get_object_or_404(Blog, sno=pk)
    analysis, _ = UserAnalyse.objects.get_or_create(user=request.user)
    if not analysis.liked_blogs.filter(pk=blog_post.pk).exists():
        analysis.liked_blogs.add(blog_post)
        blog_post.likes += 1
        liked = True
    else:
        analysis.liked_blogs.remove(blog_post)
        blog_post.likes = max(0, blog_post.likes - 1)
        liked = False

    blog_post.save()

    return JsonResponse({'likes_count': blog_post.likes, "liked": liked,
                         'message': 'Like recorded successfully'})

@login_required(login_url='/login/')
@require_POST
def add_comment(request, pk):
    try:
        data = json.loads(request.body)
        comment_body = data.get('comment_body')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON format'}, status=400)

    if not comment_body:
        return JsonResponse({'error': 'Comment body is empty'}, status=400)

    blog_post = get_object_or_404(Blog, sno=pk)
    user = request.user

    new_comment = BlogComment.objects.create(blog=blog_post, name=user, body=comment_body)

    return JsonResponse({
        'success': True,
        'comment_body': new_comment.body,
        'comment_name': new_comment.name.username,
        'comment_date': new_comment.date.strftime("%d-%m-%Y")}, status=201)
