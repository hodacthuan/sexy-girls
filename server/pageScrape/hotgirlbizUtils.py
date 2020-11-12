
import coloredlogs
import csv
import uuid
import os
import time
import random
import json

import imghdr
import datetime
from PIL import Image
import requests
from bs4 import BeautifulSoup, NavigableString
from pageScrape.models import Album, ModelInfo, Tag, Category
import requests
import logging
from sexybaby import commons, aws
import mongoengine
from sexybaby import constants
import pageScrape
from slugify import slugify
from sexybaby.commons import dataLogging, downloadAndSaveToS3, deleteTempPath, getLongId, getShortId, debug
from sexybaby.aws import deleteAwsS3Dir, uploadToAws
import logging
logger = logging.getLogger(__name__)

originUrl = 'https://hotgirl.biz'
source = 'hotgirlbiz'

coloredlogs.install()


def deleteAllImageSizeIsZeroInDBAndS3():
    albumInDB = Album.objects(albumSource=source)
    for album in albumInDB:
        for imageIndex in album['albumImages']:
            imageS3Path = 'album/' + \
                album['albumId'] + '/' + imageIndex + '.jpg'
            fileSize = aws.getObjectSize(imageS3Path)

            if fileSize == 0:
                # Delete in S3
                logger.info('Delete object: %s' % (imageS3Path))
                deleted = aws.deleteAwsS3Object(imageS3Path)

                if deleted:
                    logger.info('Delete successfully: %s' % (imageS3Path))

                # Delete in MongoDb
                newAlbumImages = album['albumImages']
                newAlbumImages.remove(imageIndex)
                logger.info('New album images array: %s' % (newAlbumImages))
                Album.objects(albumSource=source, albumId=album['albumId']).update_one(
                    set__albumImages=newAlbumImages)
                albumUpdated = Album.objects(
                    albumSource=source, albumId=album['albumId'])
                logger.info('Album images updated: %s' %
                            (albumUpdated[0]['albumImages']))


def deleteAlbumExistOnS3ButNotInDB():
    s3List = aws.listSubfolderInFolder('album/')

    for albumS3Path in s3List:
        albumId = albumS3Path.split('/')[1]
        albumInDB = Album.objects(albumId=albumId)
        if (len(albumInDB) == 0):
            logger.info('Delete album ID: %s' % (albumId))
            aws.deleteAwsS3Dir(albumS3Path)


def moveAndOrganizeS3structure():
    albumInDB = Album.objects(albumSource=source)

    for album in albumInDB:
        if not 'albumStorePath' in album:

            date = str(album['albumUpdatedDate']).split(' ')[0].split('-')
            oldStorePage = album['albumId']
            newStorePath = date[0] + '-' + date[1] + \
                '/' + date[2] + '/' + commons.getShortId()
            for imgName in album['albumImages']:
                fromPath = 'album/' + oldStorePage + '/' + imgName + '.jpg'
                toPath = 'album/' + newStorePath + '/' + imgName + '.jpg'

                aws.copyObjectByKey(fromPath, toPath)

            Album.objects(albumSource=source, albumId=album['albumId']).update_one(
                set__albumStorePath=newStorePath)

            logger.info('Finished copy album id: %s' %
                        (album['albumId']))


def deleteOldStorePathAlbum():
    albumInDB = Album.objects(albumSource=source)

    for album in albumInDB:
        if 'albumStorePath' in album:
            oldStorePath = 'album/' + album['albumId']

            deleted = aws.deleteAwsS3Dir(oldStorePath)
            if deleted:
                logger.info('Delete old album S3 dir: %s' %
                            (album['albumId']))


def correctAndSlugifyTag():
    albumInDB = Album.objects(albumSource=source)
    for album in albumInDB:
        if 'albumTags' in album:
            if len(album['albumTags']) > 0:
                newTags = []
                for tag in album['albumTags']:
                    tagInDB = Tag.objects(tagTitle=tag)
                    if not (len(tagInDB) > 0):
                        newTag = commons.getTagTitle(tag)
                        newTags.append(newTag)

                if (len(album['albumTags']) == len(newTags)):
                    print(album['albumTags'], newTags, album['albumSourceUrl'])
                    Album.objects(albumSource=source, albumSourceUrl=album['albumSourceUrl']).update_one(
                        set__albumTags=newTags)


def correctAndSlugifyCategory():
    albumInDB = Album.objects(albumSource=source)
    for album in albumInDB:
        if 'albumCategories' in album:
            if len(album['albumCategories']) > 0:
                newCategorys = []
                for tag in album['albumCategories']:
                    tagInDB = Category.objects(categoryTitle=tag)
                    if not (len(tagInDB) > 0):
                        newCategory = commons.getCategoryTitle(tag)
                        newCategorys.append(newCategory)

                if (len(album['albumCategories']) == len(newCategorys)):
                    print(album['albumCategories'],
                          newCategorys, album['albumSourceUrl'])
                    Album.objects(albumSource=source, albumSourceUrl=album['albumSourceUrl']).update_one(
                        albumCategories=newCategorys)
