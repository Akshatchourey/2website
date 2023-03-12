from django.shortcuts import render
import webbrowser
import google

def index(request):
    akshat={"search":webbrowser.open("How to increase concentration")}
    return render(request, "website/index.html",akshat)


