from django.shortcuts import render, redirect
from .models import Comment

# For login logic and comment logic.

def log_submit(request):
    return redirect(request, "/index.html/")
def sign_submit(request):
    return redirect(request, "/login.html/")


def comment(request):
    if request.method == 'GET':
        name = request.GET.get('name', None)
        email = request.GET.get("email", None)
        text = request.GET.get("queries", None)
        if name and email and text:
            obj = Comment(name=name, email=email, desc=text)
            obj.save()

    no_of_comments = 5
    comments = Comment.objects.order_by('-time')[:no_of_comments]
    context = {'comments': comments}
    return render(request, "opcoder/comment.html", context)
