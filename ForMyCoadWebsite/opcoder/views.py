from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from math import ceil as c
from .models import UserAnalyse, Blog, BlogComment, Video
from django.db.models import F
from django.db.models.expressions import RawSQL

from re import sub
import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

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

def profile(request):
    return render(request, "opcoder/profile.html")

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

    user_has_liked = False
    if request.user.is_authenticated:
        analysis, _ = UserAnalyse.objects.get_or_create(user=request.user)

        if not analysis.viewed_blogs.filter(pk=this_blog.pk).exists():
            analysis.viewed_blogs.add(this_blog)

        if analysis.liked_blogs.filter(pk=this_blog.pk).exists():
            user_has_liked = True

        # analysis = getattr(request.user, 'analysis', None)# lazy loading for speed BCZ we just need to check,not need

    context = {'post': this_blog, 'comments':comments, 'user_has_liked': user_has_liked}
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
