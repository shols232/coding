from django.shortcuts import render, redirect
import json
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.conf import settings

static = settings.STATIC_URL

@login_required
def home(request):
    return render(request, 'home.html')


def log_in(request):
        if request.method == "POST":
            username = request.POST.get('username')
            password = request.POST.get('password')
            with open("static/users.json") as json_file:
                data = json.load(json_file)
                for user in data:
                    if username == user['username'] and password == user['password']:
                        user = User.objects.create_user(id=user['id'], username=user['username'], password=user['password'])
                        login(request, user)
                        return redirect("home")
                else:
                    return render(request, "login.html", {'error': 'Invalid credentials'})
        return render(request, "login.html")
@login_required
def user_list_view(request, task_id):

    with open('static/users.json') as data_file:
        users = json.load(data_file)

        challenging_users = []
        for user in users:
            if user["id"] != int(request.user.id):
                challenging_users.append(user)
        return render(request, 'users_list_page.html', {'users': challenging_users, 'task_id': task_id})
@login_required
def task_list_view(request):

    with open('static/tasks.json') as data_file:
        tasks = json.load(data_file)
        return render(request, 'task_list.html', {'tasks': tasks})

@login_required
def user_send_request_view(request, user_id, task_id):
    request_user_id = request.user.id
    task_id = task_id
    user_id = user_id
    notification = {}

    requesting_user = {}
    with open('static/users.json') as data_file:
        first_users = json.load(data_file)
        for user in first_users:
            if user['id'] == int(request_user_id):
                requesting_user = user
            if user['id'] == int(user_id):
                user = user

        for notification in user["notifications"]:
            if notification['request_user_id'] == request_user_id and notification['task_id'] == task_id:
                return render(request, 'request_sent.html', {"sent": True})

    with open('static/tasks.json') as data_file:
        tasks = json.load(data_file)
        for task in tasks:
            if task['id'] == int(task_id):
                notification['status'] = 'pending'
                notification['message'] = f'{requesting_user["username"]} has challenged you to a duel in {task["task"]}'
                # notification['task'] = f'task: {user["task"]}'
                notification['task_id'] = int(task_id)
                notification['request_user_id'] = int(request_user_id)
                notification['user_id'] = int(user_id)

    with open('static/users.json') as json_file:
        users = json.load(json_file)

    for user in users:
        if user["id"] == int(user_id):
            user["notifications"].append(notification)
            new_user_list = users

            with open('static/users.json', 'w') as json_file:
                json.dump(new_user_list, json_file)

    return render(request, 'request_sent.html', {"sent": False})

@login_required
def notifications_view(request):
    with open('static/users.json') as data_file:
        users = json.load(data_file)
        for user in users:
            if user['id'] == int(request.user.id):
                user = user
                return render(request, 'notification.html', {'user': user, 'notifications': user['notifications']})

@login_required
def notifications_processing_view(request,user_id, task_id, notification_status):
    with open('static/users.json') as data_file:
        users = json.load(data_file)
        new_users_list = []
        for user in users:
            if user['id'] == int(request.user.id) or user['id'] == user_id:
                if notification_status == 'accept':
                    new_notifications = [notification for notification in user['notifications'] if
                                         notification['task_id'] != task_id]
                    with open('static/tasks.json') as file:
                        tasks = json.load(file)
                        user['notifications'] = new_notifications
                        for task in tasks:
                            if task['id'] == task_id:
                                new_task = task
                                if new_task in user['active']:
                                    for user_ in users:
                                        if user_['id'] == user_id:
                                            new_users_list.append(user_)
                                    new_users_list.append(user)
                                else:
                                    user['active'].append(new_task)
                                    for user_ in users:
                                        if user_['id'] == user_id:
                                            user_['active'].append(new_task)
                                            new_users_list.append(user_)
                                    new_users_list.append(user)
                elif notification_status == 'decline':
                    new_notifications = [notification for notification in user['notifications'] if notification['task_id'] != task_id ]
                    user['notifications'] = new_notifications
                    new_users_list.append(user)
            else:
                new_users_list.append(user)

        with open('static/users.json', 'w') as json_file:
            json.dump(new_users_list, json_file)

        with open('static/users.json') as json_file:
            users = json.load(json_file)
            for user in users:
                if user['id'] == request.user.id:
                    return render(request, 'challenges.html')
            else:
                return render(request, 'error.html')

@login_required
def challenges_view(request):
    with open('static/users.json') as data_file:
        users = json.load(data_file)
        for user in users:
            if user['id'] == int(request.user.id):
                user = user
                return render(request, 'challenges.html', {'user': user, 'tasks': user['active']})

def logout_view(request):
    logout(request)
    return redirect('login')

