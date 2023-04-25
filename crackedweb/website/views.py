from django.shortcuts import render
# import webbrowser, import google
from googlesearch import  search

def index(request):
    akshat={"search":search("How to increase concentration", tld="co.in", num=30, stop=30, pause=2)}
    return render(request, "website/index.html",akshat)


