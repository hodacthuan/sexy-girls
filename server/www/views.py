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


def hello(request):
    return render(request, "hello.html")


def images(request, imagePath, imageFileName):
    return serve(request, imageFileName, document_root=constants.IMAGE_STORAGE+imagePath)


def albums(request, albumTitle):
    album = Album.objects(albumTitle=albumTitle)[0]
    commons.copyAlbumFromS3ToServer(album)
    album.albumThumbnail.url = constants.BUCKET_PUBLIC_URL + \
        album.albumThumbnail.imgStorePath

    for index in range(len(album.albumImages)):

        album.albumImages[index].url = constants.BUCKET_PUBLIC_URL + \
            album.albumImages[index].imgStorePath

    print(album.albumImages[1].url)
    # dataLogging(album, '')

    context = {
        'album': album
    }
    return render(request, "album.html", context)
