import os
import json
import uuid
import time
import boto3
import shutil
import logging
import os.path
import coloredlogs
import mongoengine
import pageScrape
import urllib.request
from os import path
from slugify import slugify
from sexybaby import cache
from sexybaby.constants import *
from .aws import copyFromS3, uploadToAws
from pageScrape.models import *
from botocore.exceptions import NoCredentialsError

coloredlogs.install()
logger = logging.getLogger(__name__)
s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY,
                  aws_secret_access_key=AWS_SECRET_KEY)


def dataLogging(obj, prefix=''):
    obj = obj
    for key in obj:
        if isinstance(
                obj[key], mongoengine.base.datastructures.BaseList) and len(obj[key]) > 0:
            if isinstance(obj[key][0], pageScrape.models.ImageInfo):
                for k in range(len(obj[key])):
                    dataLogging(obj[key][k], ' '+key,)
            else:
                print(prefix, key, ':', obj[key])
        elif isinstance(obj[key], pageScrape.models.ImageInfo):
            dataLogging(obj[key], ' '+key)
        else:
            print(prefix, key, ':', obj[key])


def downloadAndSaveToS3(url, filePath, fileName):

    tempPath = '/tmp/' + filePath
    tempFile = tempPath + '/' + fileName

    if not(path.isdir(tempPath)):
        os.makedirs(tempPath)
    try:
        opener = urllib.request.URLopener()
        opener.addheader(
            'User-Agent', USER_AGENT_HEADER)
        opener.retrieve(url, tempFile)

    except OSError as e:
        print("Error: %s - %s." % (e.filename, e))

    if os.path.isfile(tempFile) and os.path.getsize(tempFile) > 0:
        return uploadToAws(
            tempFile, filePath + '/' + fileName)
    else:
        return False


def copyAlbumImagesFromS3ToServer(album):
    cacheKey = cache.typeKey['storage'] + \
        cache.functionKey['copyAlbumImagesFromS3ToServer'] + \
        album['albumTitle']
    if cache.get(cacheKey):
        return

    storePath = IMAGE_STORAGE + album['albumTitle']
    if not(path.isdir(storePath)):
        os.makedirs(storePath)

        for imageNo in album['albumImages']:
            copyFromS3(album['albumStorePath'] + '/' + imageNo + '.jpg',
                       storePath + '/' + album['albumTitle'] + '-' + imageNo + '.jpg')
    cache.setex(cacheKey, 'true', cache.ttl['month'])


def copyAlbumThumbnailFromS3ToServer(album):

    cacheKey = cache.typeKey['storage'] + \
        cache.functionKey['copyAlbumThumbnailFromS3ToServer'] + \
        album['albumTitle']
    if cache.get(cacheKey):
        return

    folderPath = THUMBNAIL_STORAGE + album['albumTitle']
    if not(path.isdir(folderPath)):
        os.makedirs(folderPath)

    for imageNo in album['albumThumbnail']:
        filePath = folderPath + '/' + \
            album['albumTitle'] + '-' + imageNo + '.jpg'

        if not(path.isfile(filePath)):
            copyFromS3(album['albumStorePath'] + '/' +
                       imageNo + '.jpg', filePath)

    cache.setex(cacheKey, 'true', cache.ttl['month'])


def deleteTempPath(filePath):
    tempPath = '/tmp/' + filePath
    try:
        shutil.rmtree(tempPath)
    except OSError as e:
        print("Error: %s - %s." % (e.filename, e.strerror))


def getLongId():
    return str(uuid.uuid4())


def getShortId():
    return str(uuid.uuid4()).split('-')[0]


def getTagTitle(tagDisplayTitle):
    tagTitle = slugify(tagDisplayTitle.strip(), to_lower=True)
    tagInDB = Tag.objects(tagTitle=tagTitle)
    if (len(tagInDB) == 0):

        tag = {
            'tagTitle': tagTitle,
            'tagDisplayTitle': tagDisplayTitle.strip()
        }
        Tag(**tag).save()

    return tagTitle


def getCategoryTitle(categoryDisplayTitle):
    categoryTitle = slugify(categoryDisplayTitle.strip(), to_lower=True)
    categoryInDB = Category.objects(categoryTitle=categoryTitle)
    if (len(categoryInDB) == 0):

        category = {
            'categoryTitle': categoryTitle,
            'categoryDisplayTitle': categoryDisplayTitle.strip()
        }
        Category(**category).save()

    return categoryTitle


def getAlbumByTag(tag):
    cacheKey = cache.modelKey['album'] + cache.functionKey['listByTag'] + tag
    albumList = cache.get(cacheKey)

    if (albumList):
        return json.loads(albumList)
    else:
        albumList = Album.objects(albumTags__contains=tag).limit(16).order_by(
            '-albumUpdatedDate').to_json()

        cache.setex(cacheKey, albumList, cache.ttl['day'])

        return Album.objects.from_json(albumList)


def getAlbumDetailByTitle(albumTitle):
    cacheKey = cache.modelKey['album'] + \
        cache.functionKey['getAlbumDetailByTitle'] + albumTitle
    albumDetail = cache.get(cacheKey)

    if (albumDetail):
        return json.loads(albumDetail)
    else:
        albumDetail = Album.objects(albumTitle=albumTitle).to_json()

        cache.setex(cacheKey, albumDetail, cache.ttl['day'])

        return json.loads(cache.get(cacheKey))


def getTagDetailByTitle(tagTitle):
    cacheKey = cache.modelKey['tag'] + \
        cache.functionKey['getTagDetailByTitle'] + tagTitle
    tagDetail = cache.get(cacheKey)

    if (tagDetail):
        return json.loads(tagDetail)
    else:
        tagDetail = Tag.objects(tagTitle=tagTitle).to_json()

        cache.setex(cacheKey, tagDetail, cache.ttl['day'])

        return Tag.objects.from_json(tagDetail)


def debug(value):
    try:
        if DEPLOY_ENV == 'local':
            logging.info(value)
    except:
        logging.info('Failed to debug')


def albumHtmlPreparation(albumList):
    results = []
    for album in albumList:
        copyAlbumThumbnailFromS3ToServer(album)

        albumData = {}
        albumData['albumUrl'] = '/album/' + album['albumTitle'] + '/01/'
        albumData['albumDisplayTitle'] = album['albumDisplayTitle']
        albumData['albumThumbnailUrl'] = '/thumbnail/' + \
            album['albumTitle'] + '/' + \
            album['albumTitle'] + '-' + \
            album['albumThumbnail'][0] + '.jpg'

        results.append(albumData)

    return results
