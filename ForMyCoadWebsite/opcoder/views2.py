from django.shortcuts import render
from .models import *

# For video logic
def video_playing(request, slug):
    videoFound = Video.objects.filter(slug=slug).first()
    context = {'name': videoFound, 'types':videoFound.source[0:5]}
    return render(request, "opcoder/video_playing.html", context)

def playlist(request):
    playlists = Playlist.objects.all()
    return render(request, "opcoder/playlist.html", {'playlists':playlists})

def plvideos(request, slug):
    videos = Video.objects.filter(slug__regex=f"^{slug}.*")
    return render(request, "opcoder/videos.html", {'videos':videos})         
