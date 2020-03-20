from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from meme_app.models import Meme, UserProfile
from datetime import datetime, timedelta, date
import random

def index(request):
    context_dict = {}
    memes = Meme.objects.all()

    # get a trending meme, random from 5 most liked in past week
    seven_days_ago = datetime.now() - timedelta(days = 7)
    recent_top_memes = memes.filter(date__range = [seven_days_ago, datetime.now()]).order_by('-likes')[:5]
    context_dict['trending_meme'] = memes[random.randint(0,len(memes) - 1)]

    # get memes to store on popular today, top up to 9 memes from today
    yesterday = datetime.now() - timedelta(days = 1)
    context_dict['popular_memes'] = memes.filter(date__range = [yesterday, datetime.now()]).order_by('-likes')[:9]

    return render(request, 'meme_app/index.html', context_dict)

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username = username, password = password)
        if user:
            login(request, user)
            return redirect(reverse('meme_app:index'))
        else:
            print(f"Invalid login details: {username}, {password}")
            return HttpResponse("Invalid login details supplied.")
    else:
        return render(request, 'meme_app/login.html')

def register(request):
    if request.method == 'POST':
        # need to read over forms in book will come back to this
        return redirect(reverse('meme_app:index'))
    else:
        return render(request, 'meme_app/register.html')

def top_memes(request):
    return render(request, 'meme_app/topmemes.html')

def user_details(request):
    return render(request, 'meme_app/userdetails.html')

def account_home(request):
    return render(request, 'meme_app/accounthome.html')

def category(request):
    return render(request, 'meme_app/category.html')

def meme(request):
    return render(request, 'meme_app/meme.html')

def meme_creator(request):
    return render(request, 'meme_app/memecreator.html')
