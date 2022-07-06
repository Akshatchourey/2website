from django.shortcuts import render

# For login logic and comment logic.

def log_submit(request):
    return render(request, "opcoder/index.html")

def sign_submit(request):
    return render(request, "opcoder/login.html")


def comment(request):
    return render(request, "opcoder/comment.html")


def comment_submit(request):
    return render(request, "opcoder/comment.html")
