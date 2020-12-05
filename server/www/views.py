import re
import os
from django.views.static import serve
from django.shortcuts import render
from django.http import HttpResponse
from pageScrape.models import Album, Category, Tag
import pageScrape
import random
from mongoengine.queryset.visitor import Q
from os import path
from sexybaby import constants, commons, cache, imageUtils
import logging
import math
from sexybaby import commons
logger = logging.getLogger(__name__)


allCategory = Category.objects()
p = int(len(allCategory)/3)
menu = {
    'categories': [allCategory[0:p], allCategory[p:2*p], allCategory[2*p:]],
}


def home(request):
    albumList = Album.objects[:16].order_by('-albumUpdatedDate')
    data = {}

    # ALBUM LIST
    data['albums'] = commons.albumHtmlPreparation(albumList)
    data['slide'] = []

    # SLIDE
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

    return render(request, 'home.html', {'data': data, 'menu': menu})


def trending(request):
    return render(request, 'trending.html')


def hello(request):
    return render(request, 'hello.html')


def getDataForTemplate(pagiNo, albumList, urlPath, albumCount):
    data = {}

    data['albums'] = commons.albumHtmlPreparation(albumList)

    # PAGINATION
    pagiMin = max([(pagiNo - 5), 0])
    pagiMax = min([(pagiMin + 9), math.ceil(albumCount /
                                            constants.MAX_IMAGES_IN_ONE_PAGE)])

    data['pagiObjs'] = []
    data['pagiObjs'].append({
        'pagiUrl': '/' + urlPath + '/' + str(format(pagiNo-1, '03d')),
        'pagiNo': 'Previous',
        'pagiStatus': 'disabled' if (pagiNo == 1) else ''
    })
    for pagiIndex in range(pagiMin, pagiMax):
        pagiObj = {
            'pagiUrl': '/' + urlPath + '/' + str(format(pagiIndex+1, '03d')),
            'pagiNo': str(pagiIndex+1),
            'pagiStatus': 'active' if (pagiIndex+1 == pagiNo) else ''
        }

        data['pagiObjs'].append(pagiObj)
    data['pagiObjs'].append({
        'pagiUrl': '/' + urlPath + '/' + str(format(pagiNo+1, '03d')),
        'pagiNo': 'Next',
        'pagiStatus': 'disabled' if (pagiMax == pagiNo) else ''
    })

    data['pageNo'] = str(format(pagiNo, '03d'))

    data['category'] = Category.objects()

    tagList = Tag.objects()
    data['tag'] = random.sample(
        set(tagList), 50)
    return data


def gallery(request, pagiNo):
    pagiNo = int(pagiNo)
    albumIndexFrom = ((pagiNo-1) * constants.MAX_IMAGES_IN_ONE_PAGE)

    albumList = Album.objects.skip(albumIndexFrom).limit(constants.MAX_IMAGES_IN_ONE_PAGE).order_by(
        '-albumUpdatedDate')

    albumListTotalNumber = Album.objects.count()

    data = getDataForTemplate(
        pagiNo, albumList, 'gallery', albumListTotalNumber)

    # BREADCRUMB
    data['breadcrumb'] = [
        {
            'title': 'Home',
            'url': '/'
        },
        {
            'title': 'Gallery',
            'url': '/gallery/001'
        },
    ]

    return render(request, 'gallery.html', {'data': data, 'menu': menu})


def category(request, categoryTitle, pagiNo):
    pagiNo = int(pagiNo)
    albumIndexFrom = ((pagiNo-1) * constants.MAX_IMAGES_IN_ONE_PAGE)

    albumList = Album.objects(albumCategories__contains=categoryTitle).skip(albumIndexFrom).limit(constants.MAX_IMAGES_IN_ONE_PAGE).order_by(
        '-albumUpdatedDate')

    albumListTotalNumber = Album.objects(
        albumCategories__contains=categoryTitle).count()

    data = getDataForTemplate(
        pagiNo, albumList, 'category/' + categoryTitle, albumListTotalNumber)

    # BREADCRUMB
    categoryList = Category.objects(categoryTitle=categoryTitle)

    data['breadcrumb'] = [
        {
            'title': 'Home',
            'url': '/'
        },
        {
            'title': 'Category',
            'url': '/category'
        },
        {
            'title': categoryList[0]['categoryDisplayTitle'],
            'url': '/category/'+categoryTitle + '/001'
        },
    ]

    return render(request, 'gallery.html', {'data': data, 'menu': menu})


def tag(request, tagTitle, pagiNo):
    pagiNo = int(pagiNo)
    albumIndexFrom = ((pagiNo-1) * constants.MAX_IMAGES_IN_ONE_PAGE)

    albumList = Album.objects(albumTags__contains=tagTitle).skip(albumIndexFrom).limit(constants.MAX_IMAGES_IN_ONE_PAGE).order_by(
        '-albumUpdatedDate')

    albumListTotalNumber = Album.objects(
        albumTags__contains=tagTitle).count()

    data = getDataForTemplate(
        pagiNo, albumList, 'tag/' + tagTitle, albumListTotalNumber)

    # BREADCRUMB
    tagList = Tag.objects(tagTitle=tagTitle)

    data['breadcrumb'] = [
        {
            'title': 'Home',
            'url': '/'
        },
        {
            'title': 'Tag',
            'url': '/tag'
        },
        {
            'title': tagList[0]['tagDisplayTitle'],
            'url': '/tag/'+tagTitle + '/001'
        },
    ]

    return render(request, 'gallery.html', {'data': data, 'menu': menu})


def about(request):
    return render(request, 'about.html')


def models(request):
    return render(request, 'models.html')


def images(request, imagePath, imageFileName):
    return serve(request, imageFileName, document_root=constants.IMAGE_STORAGE+imagePath)


def thumbnails(request, imagePath, imageFileName):
    return serve(request, imageFileName, document_root=constants.THUMBNAIL_STORAGE+imagePath)


def getListOfTagDetail(albumTags):
    tagDetailList = []
    for tagTitle in albumTags:
        tagDetailList += (commons.getTagDetailByTitle(tagTitle))

    return tagDetailList


def getRelatedAlbums(albumTags):
    albumList = []

    for tag in albumTags:
        albumList += commons.getAlbumByTag(tag)

    random.shuffle(albumList)

    results = commons.albumHtmlPreparation(albumList[0:16])

    return results


def albums(request, albumTitle, albumPage):
    data = {}

    album = commons.getAlbumDetailByTitle(albumTitle)[0]

    album['albumTagDetail'] = getListOfTagDetail(album['albumTags'])

    album['relatedAlbums'] = getRelatedAlbums(album['albumTags'])

    commons.copyAlbumImagesFromS3ToServer(album)

    album['albumImageUrls'] = []

    pagiNumber = int(albumPage)
    pagiInterval = constants.ALBUM_PAGINATION_NUMBER_OF_IMAGE
    pagiStop = pagiNumber * constants.ALBUM_PAGINATION_NUMBER_OF_IMAGE

    for imgIndex in range(len(album['albumImages'])):
        imageUrl = '/image/' + \
            album['albumTitle'] + '/' + \
            album['albumTitle'] + '-' + \
            album['albumImages'][imgIndex] + '.jpg'
        if imgIndex >= (pagiStop-pagiInterval) and imgIndex < (pagiStop):
            album['albumImageUrls'].append(imageUrl)

    pagiMax = math.ceil(len(album['albumImages'])/pagiInterval)
    album['pagiObjs'] = []
    album['pagiObjs'].append({
        'pagiUrl': '/album/' + album['albumTitle'] + '/' + str(pagiNumber-1),
        'pagiNo': 'Previous',
        'pagiStatus': 'disabled' if (1 == pagiNumber) else ''
    })

    for pagiNo in range(pagiMax):
        pagiObj = {
            'pagiUrl': '/album/' + album['albumTitle'] + '/' + str(pagiNo+1),
            'pagiNo': str(pagiNo+1),
            'pagiStatus': 'active' if (pagiNo+1 == pagiNumber) else ''
        }

        album['pagiObjs'].append(pagiObj)
    album['pagiObjs'].append({
        'pagiUrl': '/album/' + album['albumTitle'] + '/' + str(pagiNumber+1),
        'pagiNo': 'Next',
        'pagiStatus': 'disabled' if (pagiMax == pagiNumber) else ''
    })

    data['breadcrumb'] = [
        {
            'title': 'Home',
            'url': '/'
        },
        {
            'title': 'Gallery',
            'url': '/gallery/001'
        },
        {
            'title': album['albumDisplayTitle'],
            'url': '/album/' + album['albumTitle'] + '/01'
        },
    ]

    return render(request, 'album.html', {'album': album, 'data': data, 'menu': menu})
