from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, Http404
from django.views.decorators.csrf import ensure_csrf_cookie
import json

# Decorator to use built-in authentication system
from django.contrib.auth.decorators import login_required

# Used to create and manually log in a user
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
import copy

# Django transaction system so we can use @transaction.atomic
from django.db import transaction

# Imports the Message class
from socialnetwork.models import *
from socialnetwork.forms import *
from datetime import datetime, timedelta
from django.utils import timezone

#ajax request sent from the globalstream (gets all messages)
#time limited based on ajax request from window.setInterval (5 secs) so that it only updates new posts
@login_required
def get_posts(request):
    end = timezone.now();
    start = end - timedelta(seconds=5);
    json_msgs = []
    msgs = Message.objects.filter(messageTime__range=[start, end]).order_by('messageTime')#will prepend, so want to prepend the oldest first
    for msg in msgs:
        new_msg = {}
        new_msg['id'] = msg.user.pk
        new_msg['text'] = msg.text
        new_msg['messageTime'] = msg.messageTime.isoformat()
        if msg.user.person.photo:
            new_msg['photo'] = True
        else:
            new_msg['photo'] = False
        new_msg['user'] = msg.user.username
        json_msgs.append(new_msg)
    response = json.dumps(json_msgs)
    return HttpResponse(response, content_type='application/json')

#posting a comment via ajax request
@login_required
@ensure_csrf_cookie
def add_comment(request):
    user = request.user
    if not 'comm' in request.POST or not request.POST['comm']:
        message = 'You must enter a comment to add.'
        json_error = '{ "error": "'+ message +'" }'
        return HttpResponse(json_error, content_type='application/json')
    if not 'postId' in request.POST or not request.POST['postId']:
        message = 'The comment must be associated with a post!'
        json_error = '{ "error": "'+ message +'" }'
        return HttpResponse(json_error, content_type='application/json')
    comm = request.POST['comm']
    postId = request.POST['postId']
    time = timezone.now().isoformat();
    msg = Message.objects.get(id = postId)
    new_comment = Comment(comm=comm, commenter=user, msg=msg, time=time)
    new_comment.save()
    comments = list(Comment.objects.all().order_by('time').values())
    for comment in comments:
        comment['time'] = str(comment['time'])
        user = User.objects.filter(id = comment['commenter_id'])[0]
        if user.person.photo:
            comment['photo'] =True
        else:
            comment['photo'] = False
        comment['user'] = user.username #send so can easily call the username as well
    response = json.dumps(comments)
    print "repsonse: ", response
    return HttpResponse(response, content_type='application/json')

# getting all the comments (for ajax requests)
@login_required
def get_comments(request):
    comments = list(Comment.objects.all().order_by('time').values())
    for comment in comments:
        user_id = comment['commenter_id']
        comment['time'] = str(comment['time'])
        user = User.objects.filter(id = comment['commenter_id'])[0]
        if user.person.photo:
            comment['photo'] = True
        else:
            comment['photo'] = False
        username = user.username
        comment['user'] = username #send so can easily call the username as well
    response = json.dumps(comments)
    return HttpResponse(response, content_type='application/json')

#for the follow feed (ajax request): need to get only those messages for people user is following
#time limited (based on the socialnetwork.js interval of 5 secs) so we only update with new posts
@login_required
def get_feed(request):
    end = timezone.now();
    start = end - timedelta(seconds=5);
    json_msgs = []
    try:
        recentPost = Message.objects.filter(user=request.user).order_by('-messageTime')[0]
    except: 
        recentPost = ""
    following = list(request.user.person.cool_people_to_follow.all())
    followingUsers = []
    for follow in following:
        followingUsers.append(follow.user)
    msgs = Message.objects.filter(messageTime__range=[start, end], user__in=followingUsers).order_by('messageTime')#will prepend, so want to prepend the oldest first
    for msg in msgs:
        new_msg = {}
        new_msg['id'] = msg.id
        new_msg['text'] = msg.text
        new_msg['messageTime'] = msg.messageTime.isoformat()
        if msg.user.person.photo:
            new_msg['photo'] = True
        else:
            new_msg['photo'] = False
        new_msg['user'] = msg.user.username
        json_msgs.append(new_msg)
    response = json.dumps(json_msgs)
    return HttpResponse(response, content_type='application/json')

#home page redirects to the followfeed (if logged in)
@login_required
@ensure_csrf_cookie
def home(request):
    context['user'] = request.user
    return render(request, 'socialnetwork/followfeed.html', context)

#for viewing other users' profiles (accessed through the globalstream or followfeed)
@login_required
@transaction.atomic
def profile(request, id):
    try: 
        if request.method == 'GET':    
            the_user = User.objects.filter(pk=id)[0]
            context = {'user':the_user, 'id':id}#removed msgs since no longer using
            return render(request, 'socialnetwork/profile.html', context)
    except Message.DoesNotExist:
        return (redirect("followfeed")) #just stay on the global stream page in that case

#for displaying photos on profile pages 
#(after reconfiguring, this function may not be necessary-- could possibly combine with get_photo_stream)
@login_required
def get_any_photo(request, id):
    try: 
        if request.method == 'GET': 
            new_id =id      
            user = User.objects.get(id=new_id)
            person = Person.objects.get(user=user)
            if person.photo is None:
               return HttpResponse('')    
            return HttpResponse(person.photo, content_type=person.content_type)
    except Person.DoesNotExist:
        return (redirect("followfeed")) #just stay on the follow feed page in that case

#for displaying photos on the globalstream or followfeed
@login_required
def get_stream_photo(request, id):
    try: 
        if request.method == 'GET':    
            the_user = User.objects.filter(pk=id)[0]
            username = the_user.username
            msgs = Message.objects.filter(user=id).order_by('-messageTime')
            person = Person.objects.get(user=the_user)
            if person.photo is None:
                return HttpResponse('')
            return HttpResponse(person.photo, content_type=person.content_type)
    except Person.DoesNotExist:
        return (redirect("followfeed")) #just stay on the follow feed page in that case

#editing your own profile, makes use of EditProfile form
@login_required
def editprofile(request):
    context={}
    if request.method == 'GET':
        person = Person.objects.get(user=request.user)
        form = EditProfile(instance=person)
        context['form'] = form
        return render(request, 'socialnetwork/editprofile.html', context)
    person = Person.objects.get(user=request.user)
    form = EditProfile(request.POST, instance=person)
    if not form.is_valid():
        context['form'] = form
        return render(request, 'socialnetwork/editprofile.html', context)
    form.save()
    return redirect(reverse('viewprofile'))

#for viewing one's own profile
@login_required
def viewprofile(request):
    return render(request, 'socialnetwork/viewprofile.html')

#for writing a post
#sig is used to determine the page so we can redirect to the proper path
@login_required
def writepost(request, sig):
    try:
        if int(sig) == 1:
            path = "followfeed"
        else:
            path = "globalstream"
    except:
        path = "globalstream" #just take back to globalstream if it's a non integer or null
    try:
        msg = Message(user = request.user, text = request.POST['text'], messageTime = timezone.now() )
        form = MakePost(request.POST, instance=msg)
        if not form.is_valid():
            return render(request, 'socialnetwork/' + path, {'form':form})
        form.save()
        return redirect(reverse(path))
    except:
        return redirect(reverse(path))

#for the managefollows page
@login_required
def follows(request):
    context ={}
    following = list(request.user.person.cool_people_to_follow.all())
    if len(following)>0:
        messagefollow = "Here's who you follow:"
    else:
        messagefollow = ""
    not_following= Person.objects.all().exclude(user__in = following)

    not_following = not_following.exclude(user = request.user)
    if len(not_following)>0:
        message_not = "Wanna follow any of these people?"
    else:
        message_not = ""
    context['following'] = following
    context['not_following'] = not_following
    context['messagefollow'] = messagefollow
    context['message_not'] = message_not
    return render(request, 'socialnetwork/managefollows.html', context)

@login_required
def follow(request, id):
    coolUser = User.objects.get(id = id)
    coolPerson = Person.objects.get(user=coolUser)
    current_user = request.user.person
    current_user.cool_people_to_follow.add(coolPerson)
    return redirect(reverse("follows"))

@login_required
def unfollow(request, id):
    lameUser = User.objects.get(id = id)
    lamePerson = Person.objects.get(user=lameUser)
    current_user = request.user.person
    current_user.cool_people_to_follow.remove(lamePerson)
    return redirect(reverse("follows"))

# Display posts from people you follow
@login_required
@ensure_csrf_cookie
def followfeed(request):
    sig = 1 #used to signify that you're on the followfeed
    try:
        recentPost = Message.objects.filter(user=request.user).order_by('-messageTime')[0]
    except: 
        recentPost = ""
    following = list(request.user.person.cool_people_to_follow.all())
    followingUsers = []
    for follow in following:
        followingUsers.append(follow.user)
    msgs = Message.objects.filter(user__in=followingUsers )
    msgs = msgs.order_by('-messageTime')
    if len(msgs)<1:
        message = "Not much conversation here. Maybe try following more people"
    else:
        message =""
    form = MakePost()
    context = {'msgs': msgs, 'form': MakePost(), 'message':message, 'recentPost':recentPost, 'sig':sig, 'js':True}
    return render(request, 'socialnetwork/followfeed.html', context)

@login_required
@ensure_csrf_cookie
def globalstream(request):
    form = MakePost()
    msgs = Message.objects.all()
    msgs = msgs.order_by('-messageTime')
    sig = 0 # used to signify that it's the global stream (for write post)
    context = {'msgs': msgs, 'form':form, 'sig':sig, 'js':True}
    return render(request, 'socialnetwork/globalstream.html', context)

@login_required
def get_user_photo(request):
    person = Person.objects.get(user=request.user)
    if person.photo is None:
        return HttpResponse('')
    else:
        return HttpResponse(person.photo, content_type=person.content_type)

@transaction.atomic
def register(request):
    context = {}
    form = RegistrationForm()
    context['form'] = form
    if request.method == 'GET':
        form = RegistrationForm()
          # Validates the form.
        if not form.is_valid():
            return render(request, 'socialnetwork/register.html', context)

    # Creates a bound form from the request POST parameters and makes the 
    # form available in the request context dictionary.
    form = RegistrationForm(request.POST)
    context['form'] = form
    if not form.is_valid():
        return render(request, 'socialnetwork/register.html', context)
    # Creates the new user from the valid form data
    new_user = User.objects.create_user(username=request.POST['username'], 
                                        password=request.POST['password1'],
                                       )
    new_user.save()
    new_person = Person(user=new_user)
    new_person.firstname = request.POST['firstname']
    new_person.lastname=request.POST['lastname']
    new_person.save()

    # Logs in the new user and redirects to his/her todo list
    new_user = authenticate(username=request.POST['username'],
                            password=request.POST['password1'])
    
    login(request, new_user)
    return redirect(reverse('home'))




