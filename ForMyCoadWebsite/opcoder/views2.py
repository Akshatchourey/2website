from django.shortcuts import render
from .models import *
import random

# For video logic
def video_playing(request, slug):
    videoFound = Video.objects.filter(slug=slug).first()
    
    plvideos = 'None'
    if slug[3:11] != "xxxxxx00":
        plvideos = Video.objects.filter(slug__regex=f"^{slug[0:11]}.*")
    mvideos = list(Video.objects.all())
    more_videos = random.sample(mvideos, len(mvideos))
    context = {'name': videoFound, 'types':videoFound.source[0:5], 'plvideos':plvideos ,'mvideos':more_videos}
    return render(request, "opcoder/video_playing.html", context)

def playlist(request):
    playlists = Playlist.objects.all()
    return render(request, "opcoder/playlist.html", {'playlists':playlists})

def plvideos(request, slug):
    videos = Video.objects.filter(slug__regex=f"^{slug}.*")
    return render(request, "opcoder/videos.html", {'videos':videos})         
