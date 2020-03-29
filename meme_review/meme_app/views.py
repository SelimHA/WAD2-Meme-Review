from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from meme_app.models import Meme, UserProfile, Category, Comment, View
from meme_app.forms import UserForm, UserProfileForm, MemeForm, AccountForm
from datetime import datetime, timedelta, date
from django.core.paginator import Paginator
import random


def index(request):
    context_dict = {}
    memes = Meme.objects.all()
    context_dict['categories'] = Category.objects.all()

    # get a trending meme, random from 5 most liked in past week
    seven_days_ago = datetime.now() - timedelta(days = 7)
    recent_top_memes = memes.filter(date__range = [seven_days_ago, datetime.now()], nsfw = (not restrictor(request.user))).order_by('-likes')[:5]
    if(len(memes)>0):
        context_dict['trending_meme'] = memes[random.randint(0,len(memes) - 1)]
    else:
        context_dict['trending_meme'] = None

    # get memes to store on popular today, top up to 9 memes from today
    yesterday = datetime.now() - timedelta(days = 1)
    context_dict['popular_memes'] = memes.filter(date__range = [yesterday, datetime.now()]).order_by('-likes')[:9]

    return render(request, 'meme_app/index.html', context_dict)


def user_login(request):
    context_dict = {}
    context_dict['categories'] = Category.objects.all()
    if not request.user.is_authenticated:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(username = username, password = password)
            if user:
                login(request, user)
                return redirect(reverse('index'))
            else:
                messages.error(request, "Username or password is incorrect")
                return redirect(reverse('login'))
        else:
            return render(request, 'meme_app/login.html', context_dict)
    else:
        return redirect(reverse('index'))


@login_required(login_url='login')
def user_logout(request):
    logout(request)
    return redirect(reverse('index'))


def register(request):
    if not request.user.is_authenticated:
        registered = False

        if request.method == 'POST':
            user_form = UserForm(request.POST)
            profile_form = UserProfileForm(request.POST)

            if user_form.is_valid() and profile_form.is_valid():
                user = user_form.save()
                user.set_password(user.password)
                user.save()
                profile = profile_form.save(commit = False)
                profile.user = user
                profile.save()
                registered = True
            else:
                print(user_form.errors, profile_form.errors)
        else:
            user_form = UserForm()
            profile_form = UserProfileForm()

        context_dict = {
            'user_form' : user_form,
            'profile_form' : profile_form,
            'registered' : registered,
            'categories' : Category.objects.all()
        }
        return render(request, 'meme_app/register.html', context_dict)
    else:
        return redirect(reverse('index'))


def top_memes(request):
    context_dict = {}
    memes = Meme.objects.all().filter(nsfw = (not restrictor(request.user)))
    context_dict['categories'] = Category.objects.all()

    # gets the top 9 memes of all time
    context_dict['top_memes'] = [{"name": "Top memes", "memes":memes.order_by('-likes')[:9]}]

    return render(request, 'meme_app/topmemes.html', context_dict)


def account(request, username):
    context_dict = {}
    context_dict['categories'] = Category.objects.all()
    try:
        user = UserProfile.objects.get(user__username = username)
        context_dict['profile'] = user
    except:
        return render(request, '404.html', context_dict)

    if request.user.username == username:
        memes = Meme.objects.all().filter(user = user)
    else:
        memes = Meme.objects.all().filter(user = user, nsfw = (not restrictor(request.user)))
    context_dict['memes'] = memes
    context_dict['meme_total'] = len(memes)
    context_dict['likes_total'] = sum([meme.likes for meme in memes])
    context_dict['dislikes_total'] = sum([meme.dislikes for meme in memes])

    if request.user.username == username:
        if request.method == 'POST':
            profile_form = AccountForm(request.POST)
            if profile_form.is_valid():
                user.bio = request.POST.get('bio')
                if 'picture' in request.FILES:
                    user.picture = request.FILES['picture']
                user.save()
            else:
                print(profile_form.errors)

        context_dict['profile_form'] = AccountForm(instance = user)

    context_dict['img_url'] = user.picture
    return render(request, 'meme_app/account.html', context_dict)


def category(request, cat):
    context_dict = {}
    context_dict['categories'] = Category.objects.all()
    # checks if the category exists
    try:
        cat_obj = Category.objects.get(name = cat)
    except:
        return render(request, '404.html', context_dict)

    # gets memes with a specific category
    memes = Meme.objects.all().filter(category = cat_obj, nsfw = (not restrictor(request.user)))
    if not memes:
        context_dict['has_memes'] = False
    else:
        context_dict['has_memes'] = True
    paginator = Paginator(memes, 9) # 9 meme per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context_dict['page'] = page_obj
    context_dict['category'] = cat
    return render(request, 'meme_app/category.html', context_dict)


def meme(request, id):
    context_dict = {}
    context_dict['categories'] = Category.objects.all()
    # try and store meme in context dictionary
    try:
        meme = Meme.objects.get(id = id)
        context_dict['meme'] = meme
        context_dict['comments'] = Comment.objects.all().filter(meme = context_dict['meme'])
        # check user session id and add the view to the meme
        if not request.session.session_key:
            request.session.save()
        key = request.session.session_key
        views = View.objects.filter(meme = meme, viewer_id = key)
        if not views:
            views = View(viewer_id = key, meme = meme)
            views.save()
            meme.views += 1
            meme.save()
    except:
        return render(request, '404.html', context_dict)
    return render(request, 'meme_app/meme.html', context_dict)


@login_required(login_url='login')
def meme_creator(request):
    if request.method == 'POST':
        meme_form = MemeForm(request.POST)

        if meme_form.is_valid():
            meme = meme_form.save(commit = False)
            meme.user = UserProfile.objects.get(user = request.user)
            meme.picture = request.FILES['picture']
            meme.save()
            return redirect(reverse('meme', args = [meme.id]))
        else:
            print(meme_form.errors)
    else:
        meme_form = MemeForm()

    context_dict = {'meme_form' : meme_form, 'categories' : Category.objects.all()}
    return render(request, 'meme_app/memecreator.html', context_dict)


def about(request):
    context_dict = {}
    context_dict['categories'] = Category.objects.all()
    return render(request,'meme_app/about.html', context_dict)


def unsupported(request):
    return render(request,'unsupported.html')


def rate(request, id, type):
    context_dict = {}
    context_dict['categories'] = Category.objects.all()
    try:
        meme = Meme.objects.get(id = id)
    except:
        render(request, '404.html', context_dict)
    value = request.GET.get('value')
    print(type)
    if value == '1':
        meme.likes += 1
    elif type == '0':
        meme.dislikes += 1
    meme.save()
    return redirect(reverse('meme', args = [meme.id]))


def restrictor(user):
    if not user.is_authenticated:
        return True
    else:
        try:
            user = UserProfile.objects.get(user__username == user.username)
            age_years = (date.today() - user.dob).days / 365.25
            if age_years > 18:
                return False
            else:
                return True
        except:
            return True
