import os
import re
from django.shortcuts import render
from django.http import HttpResponseRedirect
from .models import *
from sexybaby.models import *
from sexybaby.constants import *
import bcrypt
from pageScrape.models import Album, Category, Tag
from sexybaby import constants, commons, cache, imageUtils
salt = bcrypt.gensalt(rounds=4)
print(salt)

# Create your views here.


def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = UserModel.objects(
                email=form.cleaned_data['email'])

            if user and (bcrypt.checkpw(form.cleaned_data['password'].encode('utf-8'), user[0]['password'].encode('utf-8'))):
                return HttpResponseRedirect('/admin/dashboard')

        return HttpResponseRedirect('/admin/login')

    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})


def password(request):
    return render(request, 'password.html')


def register(request):
    if request.method == 'POST':
        print('come here')
        form = RegisterForm(request.POST)
        if form.is_valid():
            if REGISTER_TOKEN == form.cleaned_data['registerToken']:
                passwordHashed = bcrypt.hashpw(
                    form.cleaned_data['password'].encode('utf-8'), salt)

                user = {
                    'email': form.cleaned_data['email'],
                    'password': passwordHashed,
                    'firstName': form.cleaned_data['firstName'],
                    'lastName': form.cleaned_data['lastName']
                }

                UserModel(**user).save()

                return HttpResponseRedirect('/admin/dashboard')

        return HttpResponseRedirect('/admin/register')

    else:
        form = RegisterForm()

    return render(request, 'register.html', {'form': form})


def dashboard(request):

    data = {}
    data['cards'] = [
        {
            'title': 'Album Status',
            'link': '/admin/database/album',
            'background': 'bg-primary'
        },
        {
            'title': 'Warnning',
            'link': '/admin/database/warnning',
            'background': 'bg-warning'
        },
        {
            'title': 'Errors',
            'link': '/admin/database/errors',
            'background': 'bg-danger'
        },
        {
            'title': 'Total Views',
            'link': '/admin/database/views',
            'background': 'bg-success'
        }
    ]

    return render(request, 'dashboard.html', {'data': data})


def databaseAlbum(request):
    albumList = Album.objects.limit(
        constants.MAX_IMAGES_IN_ONE_PAGE).order_by('-albumUpdatedDate')

    data = {}
    data['albums'] = commons.albumHtmlPreparation(albumList)
    data['headers'] = ['Title', 'Tags', 'Categories']

    return render(request, 'databaseAlbum.html', {'data': data})
