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
coloredlogs.install()

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


def deleteAwsS3Dir(s3FilePath):
    try:
        s3.delete_object(
            Bucket=constants.AWS_BUCKET,
            Key=s3FilePath
        )

        return True
    except FileNotFoundError:
        print("The file was not found")
        return False
    except NoCredentialsError:
        print("Credentials not available")
        return False


def uploadToAws(filePath, s3FilePath):

    try:
        s3.upload_file(filePath, constants.AWS_BUCKET, s3FilePath, ExtraArgs={
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
    try:
        urllib.request.urlretrieve(url, tempFile)
    except OSError as e:
        print("Error: %s - %s." % (e.filename, e.strerror))

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


def debug(value):
    try:
        environment = os.environ['ENVIRONMENT']
        if environment == 'development':
            logging.info(value)
    except:
        logging.info('Failed to debug')
