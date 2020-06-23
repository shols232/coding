from django.shortcuts import render, redirect
import json
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.conf import settings

static = settings.STATIC_URL


def home(request):
    print(request.user.id)
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
                        global logged_in_user
                        logged_in_user = user
                        return redirect("home")
                else:
                    return render(request, "login.html", {'error': 'Invalid credentials'})
        try:
            if logged_in_user:
                with open('static/users.json') as data_file:
                    users = json.load(data_file)
                    global updated_users_list
                    updated_users_list = [logged_in_user if user['id'] == logged_in_user['id'] else user for user in users ]
                    for user in users:
                        if user['id'] == int(logged_in_user['id']):
                            return redirect("home", {'user_id':logged_in_user['id']})

                with open('static/users.json', 'w') as data_file:
                    json.dump(updated_users_list, data_file)
        except NameError:
            pass

        return render(request, "login.html")

def user_list_view(request, task_id):

    with open('static/users.json') as data_file:
        users = json.load(data_file)

        challenging_users = []
        for user in users:
            if user["id"] != int(request.user.id):
                challenging_users.append(user)
        print(challenging_users[:3])
        return render(request, 'users_list_page.html', {'users': challenging_users, 'requesting_user_id': request.user.id, 'task_id': task_id})

def task_list_view(request):

    with open('static/tasks.json') as data_file:
        tasks = json.load(data_file)
        return render(request, 'task_list.html', {'tasks': tasks})

def user_send_request_view(request, request_user_id, task_id, user_id):
    request_user_id = request_user_id
    task_id = task_id
    user_id = user_id
    notification = {}

    requesting_user = {}
    print(user_id, task_id, request_user_id)
    with open('static/users.json') as data_file:
        first_users = json.load(data_file)
        for user in first_users:
            if user['id'] == int(request_user_id):
                requesting_user = user
            if user['id'] == int(user_id):
                user = user
                print(user)

        for notification in user["notifications"]:
            if notification['request_user_id'] == request_user_id and notification['task_id'] == task_id:
                print('hello1')
                return render(request, 'request_sent.html', {"sent": True})

    with open('static/tasks.json') as data_file:
        tasks = json.load(data_file)
        for task in tasks:
            if task['id'] == int(task_id):
                print('holla')
                notification['status'] = 'pending'
                notification['message'] = f'Hello {user["username"]}, {requesting_user["username"]} has challenged you to a duel in {task["task"]}'
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

    print('hello 2')
    return render(request, 'request_sent.html', {"sent": False})

def notifications_view(request):
    print(request.user)
    with open('static/users.json') as data_file:
        users = json.load(data_file)
        for user in users:
            if user['id'] == int(request.user.id):
                user = user
                return render(request, 'notification.html', {'user': user, 'notifications': user['notifications']})

def notifications_processing_view(request, user_id, task_id, notification_status):
    current_user = None
    with open('static/users.json') as data_file:
        users = json.load(data_file)
        new_users_list = []
        for user in users:
            if user['id'] == int(user_id):
                current_user = user
                if notification_status == 'accept':
                    with open('static/tasks.json') as file:
                        tasks = json.load(file)
                        for task in tasks:
                            if task['id'] == task_id:
                                new_task = task
                                if new_task in user['active']:
                                    pass
                                else:
                                    user['active'].append(new_task)
                                new_users_list.append(user)
                elif notification_status == 'decline':
                    new_notifications = [notification for notification in user['notifications'] if notification['task_id'] != task_id ]
                    user['notifications'] = new_notifications
                    new_users_list.append(user)
            else:
                new_users_list.append(user)

    print(new_users_list)
    with open('static/users.json', 'w') as json_file:
        json.dump(new_users_list, json_file)
    if current_user:
        return render(request, 'challenges.html', {'user': current_user, 'tasks': current_user['active']})
    else:
        return render(request, 'error.html')

def challenges_view(request):
    with open('static/users.json') as data_file:
        users = json.load(data_file)
        for user in users:
            if user['id'] == int(request.user.id):
                user = user
                return render(request, 'challenges.html', {'user': user, 'tasks': user['active']})

