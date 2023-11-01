from django.shortcuts import render, redirect

# For login logic and comment logic.

def log_submit(request):
    return redirect(request, "/index.html/")

def sign_submit(request):
    return redirect(request, "/login.html/")


def comment(request):
    return render(request, "opcoder/comment.html")


def comment_submit(request):
    return render(request, "opcoder/comment.html")
