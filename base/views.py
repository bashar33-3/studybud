from django.shortcuts import render, redirect, HttpResponse
from django.db.models import Q
from .models import Room, Topic, Message
from .forms import RoomForm, UserForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
# Create your views here.

# rooms =[
#     {'id':1, 'name':'Lets learn Python'},
#     {'id':2, 'name':'Design with me'},
#     {'id':3, 'name':'Frontend devs'},
# ]


def loginPage(request):
    page = 'login'

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist.')

        user = authenticate(request, username=username, password=password)
    
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username or Password does not exist.')


    context = {'page':page}
    return render(request, 'base/login_register.html', context)


def registerUser(request):
    form = UserCreationForm()

    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        
        else:
            messages.error(request, "An error occured during registartion, please try again")

    context = {'form': form}
    return render(request, 'base/login_register.html', context)

def logoutUser(request):
    logout(request)
    return redirect('home')

def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''

    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q)|
        Q(name__icontains=q)) #get all the rooms in the database
    
    rooms_count = rooms.count()
    topics = Topic.objects.all()[0:5]
    # ## we can either order itt here like this or we can order it in the model class using META, check models.py:
    # room_messages = Message.objects.all().order_by('-created')

    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))

    context = {'rooms': rooms, 'topics': topics, 'rooms_count':rooms_count, 'room_messages': room_messages} 
    return render(request, 'base/home.html', context)

def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all().order_by('-created')
    # Many to many relationship can be get by: while many to one or one to many can be get like the above ---> room.message_set.all()
    participants = room.participants.all()

    if request.method == "POST":
        message = Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)
    
    #this is how we get all childer for the parent _set.all()
    context = {'room': room, 'room_messages': room_messages, 'participants':participants}
    return render(request, 'base/room.html', context)

def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = Room.objects.filter(host=user)
    topics = Topic.objects.all()
    # room_messages = Message.objects.filter(user=user) or
    room_messages = user.message_set.all()
    rooms_count = Room.objects.filter(host=user).count()


    context={'user':user, 'rooms':rooms, 'topics': topics, 'room_messages':room_messages,
             'rooms_count': rooms_count}
    return render(request, 'base/profile.html', context)

@login_required(login_url='login')
def updateProfile(request):
    user = request.user
    form  = UserForm(instance=user)

    if request.method == "POST":
        form = UserForm(request.POST, instance=user)
        # like above or below works
        # user.username = request.POST.get('username')
        # user.email = request.POST.get('email')
        if form.is_valid():
            form.save()
            user.save()
            return redirect('user-profile', pk=user.id)
    context = {'form': form}
    return render(request, 'base/edit-user.html', context)


@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()

    if request.method == "POST":
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)

        Room.objects.create(
            host= request.user,
            topic = topic,
            name= request.POST.get('name'),
            description= request.POST.get('description')
        )

        # form = RoomForm(request.POST)
        # if form.is_valid():
        #     room = form.save(commit=False)
        #     room.host = request.user
        #     room.save()
        return redirect('home')


    context = {'form': form, 'topics': topics}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def updateRoom(request, pk):
    #get the room we are updating
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()

    if request.user != room.host:
        return HttpResponse('You are not allowed here !!!')

    if request.method == "POST":
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name= request.POST.get('name')
        room.topic= topic
        room.description= request.POST.get('description')
        room.save()


    context = {'form': form, 'room': room, "topics": topics}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)


    if request.user != room.host:
        return HttpResponse('You are not allowed here !!!')
    

    if request.method == "POST":
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj':room})


@login_required(login_url='login')
def deleteMessage(request, pk):
    room_message = Message.objects.get(id=pk)

    if request.method == "GET":
        prev_referrer = request.META.get('HTTP_REFERER')
        request.session['previous_referrer'] = prev_referrer

    if request.user != room_message.user:
        return HttpResponse('You are not allowed here !!!')
    
    if request.method == "POST":
        room_message.delete()

        referrer = request.session.get('previous_referrer')

        if 'room' in referrer:
            return redirect('room', room_message.room_id)
        else:
            return redirect('home')
    
    return render(request, 'base/delete.html', {'obj': room_message})


def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)

    context = { 'topics': topics }
    return render(request, 'base/topics.html', context)

def activityPage(request):
    room_messages = Message.objects.all()

    context = { 'room_messages': room_messages }
    return render(request, 'base/activity.html', context)