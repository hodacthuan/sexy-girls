import logging
import mongoengine
import page_scrape
import boto3
import uuid
import time
import shutil
import os.path
from os import path
import os
from botocore.exceptions import NoCredentialsError
import urllib.request

AWS_BUCKET = 'sexy-girls-bucket'
AWS_ACCESS_KEY = os.environ['ADMIN_ACCESS_KEY_ID']
AWS_SECRET_KEY = os.environ['ADMIN_SECRET_ACCESS_KEY']


def dataLogging(obj, prefix=''):
    obj = obj
    for key in obj:
        if isinstance(
                obj[key], mongoengine.base.datastructures.BaseList) and len(obj[key]) > 0:
            if isinstance(obj[key][0], page_scrape.models.ImageInfo):
                for k in range(len(obj[key])):
                    dataLogging(obj[key][k], ' '+key,)
            else:
                print(prefix, key, ':', obj[key])
        elif isinstance(obj[key], page_scrape.models.ImageInfo):
            dataLogging(obj[key], ' '+key)
        else:
            print(prefix, key, ':', obj[key])


def uploadToAws(filePath, s3FilePath):
    s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY,
                      aws_secret_access_key=AWS_SECRET_KEY)

    try:
        s3.upload_file(filePath, AWS_BUCKET, s3FilePath, ExtraArgs={
                       'ContentType': 'image/jpeg'})
        return True
    except FileNotFoundError:
        print("The file was not found", filePath)
        return False
    except NoCredentialsError:
        print("Credentials not available")
        return False


def downloadAndSave(url, filePath, fileName):

    tempPath = '/tmp/' + filePath
    tempFile = '/tmp/' + filePath + '/' + fileName

    if not(path.isdir(tempPath)):
        os.makedirs(tempPath)

    urllib.request.urlretrieve(
        url, tempFile)

    return uploadToAws(
        tempFile, filePath + '/' + fileName)


def deleteTempPath(filePath):
    tempPath = '/tmp/' + filePath
    try:
        shutil.rmtree(tempPath)
    except OSError as e:
        print("Error: %s - %s." % (e.filename, e.strerror))


def getAlbumId():
    return str(uuid.uuid4())


def getImgId():
    return str(uuid.uuid4()).split('-')[0]
