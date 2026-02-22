from django.shortcuts import render, redirect, get_object_or_404
from .models import UserAnalyse, Playlist, Video, VideoComment
from django.db.models import F
from math import ceil as c
import random
import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.db.models.expressions import RawSQL

# For video and profile logic.

def show_videos(request, videos):
    no_of_videos = 12
    page = request.GET.get('page')
    if page is None:
        page = 1
    else:
        page = int(page)

    length = len(videos)
    videos = videos[(page-1)*no_of_videos: page*no_of_videos]
    if page > 1:
        prev = page-1
    else:
        prev = None
    if page < c(length/no_of_videos):
        nxt = page + 1
    else:
        nxt = None
    context = {'videos': videos, 'prev': prev, 'nxt': nxt}
    return render(request, "opcoder/videos.html", context)


def video(request):
    videos = Video.objects.all().order_by('-date')
    return show_videos(request, videos)


def category(request, factor):
    fts_rank_sql = "MATCH (categories) AGAINST (%s IN BOOLEAN MODE)"
    videos = Video.objects.annotate(
        rank=RawSQL(fts_rank_sql, (factor,))
    ).filter(rank__gt=0).order_by('-rank', '-tviews')

    return show_videos(request, videos)


def plvideos(request, slug):
    videos = Video.objects.filter(playlist__slug=slug).order_by('-date')
    return show_videos(request, videos)


def playlists(request):
    all_playlists = Playlist.objects.all()
    return render(request, "opcoder/playlist.html", {'playlists':all_playlists})


def video_playing(request, slug):
    video_found = get_object_or_404(Video,slug=slug)
    comments = video_found.videoComment.all().order_by("-date")
    Video.objects.filter(pk=video_found.pk).update(tviews=F('tviews') + 1)

    user_has_liked = False
    if request.user.is_authenticated:
        analysis, _ = UserAnalyse.objects.get_or_create(user=request.user)

        if not analysis.viewed_videos.filter(pk=video_found.pk).exists():
            analysis.viewed_videos.add(video_found)
            analysis.update_category_score(video_found.categories, increment_value=1)

        if analysis.liked_videos.filter(pk=video_found.pk).exists():
            user_has_liked = True

    more_videos = Video.objects.filter(visi=True)

    pl_videos = 'None'
    if video_found.playlist:
        pl_videos = Video.objects.filter(playlist=video_found.playlist)
        more_videos = more_videos.exclude(playlist=video_found.playlist)

    # fetching related videos
    factor = video_found.categories
    fts_rank_sql = "MATCH (categories) AGAINST (%s IN BOOLEAN MODE)"
    more_videos = more_videos.annotate(
        rank=RawSQL(fts_rank_sql, (factor,))
    ).filter(rank__gt=0).order_by('-rank', '-tviews')[:10]

    context = {'name': video_found, 'types':video_found.source[8:23], 'comments':comments, 'user_has_liked': user_has_liked, 'plvideos':pl_videos, 'mvideos':more_videos}
    return render(request, "opcoder/video_playing.html", context)


@login_required(login_url='/login/')
@require_POST
def like_video(request, pk):
    video_found = get_object_or_404(Video, sno=pk)
    analysis, _ = UserAnalyse.objects.get_or_create(user=request.user)
    if not analysis.liked_videos.filter(pk=video_found.pk).exists():
        analysis.liked_videos.add(video_found)
        analysis.update_category_score(video_found.categories, increment_value=2)
        video_found.tlikes += 1
        liked = True
    else:
        analysis.liked_videos.remove(video_found)
        analysis.update_category_score(video_found.categories, increment_value=-2)
        video_found.tlikes = max(0, video_found.tlikes - 1)
        liked = False

    video_found.save()

    return JsonResponse({'likes_count': video_found.tlikes, "liked": liked,
                         'message': 'Like recorded successfully'})


@login_required(login_url='/login/')
@require_POST
def comment_video(request, pk):
    try:
        data = json.loads(request.body)
        comment_body = data.get('comment_body')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON format'}, status=400)

    if not comment_body:
        return JsonResponse({'error': 'Comment body is empty'}, status=400)

    video_post = get_object_or_404(Video, sno=pk)
    user = request.user

    new_comment = VideoComment.objects.create(video=video_post, name=user, body=comment_body)

    return JsonResponse({
        'success': True,
        'comment_body': new_comment.body,
        'comment_name': new_comment.name.username,
        'comment_date': new_comment.date.strftime("%d-%m-%Y")}, status=201)
