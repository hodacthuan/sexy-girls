from django.shortcuts import render
from django.http import HttpResponse
from pageScrape.models import Album
import pageScrape
from pageScrape.commons import dataLogging
from sexybaby import constants


def index(request):
    return HttpResponse("Hello, world. ")


def album(request, albumId):
    print('albumId', albumId)
    album = Album.objects(id=albumId)[0]
    print(album.albumThumbnail.imgSourceUrl)
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
