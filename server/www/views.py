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
import math
from sexybaby import commons
logger = logging.getLogger(__name__)


def home(request):
    albumList = Album.objects[:16].order_by('-albumUpdatedDate')
    data = {}
    data['albums'] = []
    for album in albumList:
        commons.copyAlbumThumbnailFromS3ToServer(album)

        albumData = {}
        albumData['albumUrl'] = '/album/' + album['albumTitle'] + '/01/'
        albumData['albumDisplayTitle'] = album['albumDisplayTitle']
        albumData['albumThumbnailUrl'] = '/thumbnail/' + \
            album.albumTitle + '/' + \
            album.albumTitle + '-' + \
            album.albumThumbnail[0] + '.jpg'

        data['albums'].append(albumData)

    return render(request, 'home.html', {'data': data})


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


def thumbnails(request, imagePath, imageFileName):
    return serve(request, imageFileName, document_root=constants.THUMBNAIL_STORAGE+imagePath)


def albums(request, albumTitle, albumPage):
    album = Album.objects(albumTitle=albumTitle)[0]

    commons.copyAlbumImagesFromS3ToServer(album)

    album.albumImageUrls = []

    pagiNumber = int(albumPage)
    pagiInterval = constants.ALBUM_PAGINATION_NUMBER_OF_IMAGE
    pagiStop = pagiNumber * constants.ALBUM_PAGINATION_NUMBER_OF_IMAGE

    for imgIndex in range(len(album.albumImages)):
        imageUrl = '/image/' + \
            album.albumTitle + '/' + \
            album.albumTitle + '-' + \
            album.albumImages[imgIndex] + '.jpg'
        if imgIndex >= (pagiStop-pagiInterval) and imgIndex < (pagiStop):
            album.albumImageUrls.append(imageUrl)

    pagiMax = math.ceil(len(album.albumImages)/pagiInterval)
    album.pagiObjs = []
    album.pagiObjs.append({
        'pagiUrl': '/album/' + album.albumTitle + '/' + str(pagiNumber-1),
        'pagiNo': 'Previous',
        'pagiStatus': 'disabled' if (1 == pagiNumber) else ''
    })
    for pagiNo in range(pagiMax):
        pagiObj = {
            'pagiUrl': '/album/' + album.albumTitle + '/' + str(pagiNo+1),
            'pagiNo': str(pagiNo+1),
            'pagiStatus': 'active' if (pagiNo+1 == pagiNumber) else ''
        }

        album.pagiObjs.append(pagiObj)
    album.pagiObjs.append({
        'pagiUrl': '/album/' + album.albumTitle + '/' + str(pagiNumber+1),
        'pagiNo': 'Next',
        'pagiStatus': 'disabled' if (pagiMax == pagiNumber) else ''
    })

    context = {
        'album': album
    }
    return render(request, "album.html", context)
