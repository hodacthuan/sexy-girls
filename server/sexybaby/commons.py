from .aws import uploadToAws
from sexybaby import constants
import logging
import mongoengine
import pageScrape
import boto3
import uuid
import time
import shutil
import os.path
from os import path
import coloredlogs
import os
from botocore.exceptions import NoCredentialsError
import urllib.request
from .aws import copyFromS3
coloredlogs.install()
logger = logging.getLogger(__name__)
s3 = boto3.client('s3', aws_access_key_id=constants.AWS_ACCESS_KEY,
                  aws_secret_access_key=constants.AWS_SECRET_KEY)


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
    tempFile = '/tmp/' + filePath + '/' + fileName

    if not(path.isdir(tempPath)):
        os.makedirs(tempPath)
    try:

        opener = urllib.request.URLopener()
        opener.addheader(
            'User-Agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36')
        opener.retrieve(url, tempFile)
        # urllib.request.urlretrieve(url, tempFile)

    except OSError as e:
        print("Error: %s - %s." % (e.filename, e))

    return uploadToAws(
        tempFile, filePath + '/' + fileName)


def copyAlbumFromS3ToServer(album):
    storePath = constants.IMAGE_STORAGE + album['albumTitle']
    if not(path.isdir(storePath)):
        os.makedirs(storePath)

        for imageNo in album['albumImages']:
            copyFromS3('album/' + album['albumId'] + '/' + imageNo + '.jpg',
                       storePath + '/' + album['albumTitle'] + '-' + imageNo + '.jpg')

    storePathThumbnail = constants.THUMBNAIL_STORAGE + album['albumTitle']
    if not(path.isdir(storePathThumbnail)):
        os.makedirs(storePathThumbnail)

        for imageNo in album['albumThumbnail']:
            copyFromS3('album/' + album['albumId'] + '/' + imageNo + '.jpg',
                       storePath + '/' + album['albumTitle'] + '-' + imageNo + '.jpg')


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


def debug(value):
    try:
        environment = os.environ['ENVIRONMENT']
        if environment == 'development':
            logging.info(value)
    except:
        logging.info('Failed to debug')
