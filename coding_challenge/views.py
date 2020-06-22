
from django.shortcuts import render,redirect
import json
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required

#@login_required(login_url ="login")
def home(request):
    return render(request, 'home.html')


def log_in(request):
    with open("users.json") as json_file:
        data = json.load(json_file)

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        for user in range(len(data)):
            if username == data[user]['username'] and password == data[user]['password']:
                return redirect("home")
            else:
                messages.error(request, "Invalid details")


        
    #
    return render(request, "index.html")

