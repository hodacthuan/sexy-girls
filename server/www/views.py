import re
import os
from django.views.static import serve
from django.shortcuts import render
from django.http import HttpResponse
from pageScrape.models import Album
import pageScrape
import random
from os import path
from sexybaby import imageUtils
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
    data['slide'] = []
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
    existingAlbums = []
    for album in albumList:
        albumPath = constants.IMAGE_STORAGE + album['albumTitle']
        if path.isdir(albumPath):
            existingAlbums.append(album)

    # random.shuffle(existingAlbums)

    for album in existingAlbums:
        albumPath = constants.IMAGE_STORAGE + album['albumTitle']
        if (len(data['slide']) < 5):

            slideVerticalImages = []
            slideHorizontalImages = []

            imgIndex = 0
            while (imgIndex < (len(album['albumImages'])-5)):
                imgIndex += 1

                imagePath = albumPath + '/' + album['albumTitle'] + \
                    '-' + album['albumImages'][imgIndex] + '.jpg'

                if path.exists(imagePath):
                    imageSize = imageUtils.getImageSize(imagePath)

                    if (imageSize[0] < imageSize[1]) and (imageSize[0] > 500) and (imageSize[1] > 500):
                        slideVerticalImages.append(
                            album['albumImages'][imgIndex])
                    else:
                        slideHorizontalImages.append(
                            album['albumImages'][imgIndex])

            if ((len(slideVerticalImages) >= 2) and (len(slideHorizontalImages) >= 1)):
                randomSlideVerticalImages = random.sample(
                    set(slideVerticalImages), 2)

                sliceImageData = []
                sliceImageData.append(
                    '/image/'+album['albumTitle'] + '/' + album['albumTitle'] +
                    '-' + randomSlideVerticalImages[0]+'.jpg')
                sliceImageData.append(
                    '/image/'+album['albumTitle'] + '/' + album['albumTitle'] +
                    '-' + random.choice(slideHorizontalImages)+'.jpg')
                sliceImageData.append(
                    '/image/'+album['albumTitle'] + '/' + album['albumTitle'] +
                    '-' + randomSlideVerticalImages[1]+'.jpg')

                data['slide'].append(
                    {
                        'images': sliceImageData,
                        'albumDisplayTitle': album['albumDisplayTitle'],
                        'albumTitle': album['albumTitle'],
                        'status': 'active' if (len(data['slide']) == 0) else '',
                        'slideNo': len(data['slide']),
                        'albumUrl': '/album/' + album['albumTitle'] + '/01/'
                    })

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
