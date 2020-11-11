import re
import os
from django.views.static import serve
from django.shortcuts import render
from django.http import HttpResponse
from pageScrape.models import Album
import pageScrape
from sexybaby.commons import dataLogging
from sexybaby import constants
import logging
from sexybaby import commons
logger = logging.getLogger(__name__)


def home(request):
    return render(request, "home.html")


def trending(request):
    return render(request, "trending.html")


def hello(request):
    return render(request, "hello.html")


def gallery(request):
    return render(request, "gallery.html")


def about(request):
    return render(request, "about.html")


def models(request):
    return render(request, "models.html")


def images(request, imagePath, imageFileName):
    return serve(request, imageFileName, document_root=constants.IMAGE_STORAGE+imagePath)


def albums(request, albumTitle):
    album = Album.objects(albumTitle=albumTitle)[0]

    commons.copyAlbumFromS3ToServer(album)

    album.albumImageUrls = []
    for imgNo in album.albumImages:

        imageUrl = '/image/' + \
            album.albumTitle + '/' + \
            album.albumTitle + '-' + \
            imgNo + '.jpg'
        album.albumImageUrls.append(imageUrl)

    context = {
        'album': album
    }
    return render(request, "album.html", context)
