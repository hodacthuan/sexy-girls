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


def deleteAwsS3Dir(s3FilePath):
    try:
        objectKeys = listAllObjectsInFolder(s3FilePath)

        for objectKey in objectKeys:
            deleteAwsS3Object(objectKey)

        return True
    except FileNotFoundError:
        print("The file was not found")
        return False
    except NoCredentialsError:
        print("Credentials not available")
        return False

def deleteAwsS3Object(s3FilePath):
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

def getObjectSize( s3FilePath):
   
    try:
        response = s3.head_object(
            Bucket=constants.AWS_BUCKET,
            Key=s3FilePath)
        size = response['ContentLength']
        return size
    except FileNotFoundError:
        print("The file was not found", filePath)
        return False
    except NoCredentialsError:
        print("Credentials not available")
        return False

def listAllObjectsInFolder(prefix):
    """Get a list of all keys in an S3 bucket."""
    keys = []
    kwargs = {
        'Bucket': constants.AWS_BUCKET,
        'Prefix': prefix
    }

    while True:
        resp = s3.list_objects_v2(**kwargs)
        
        for obj in resp['Contents']:
            keys.append(obj['Key'])

        try:
            kwargs['ContinuationToken'] = resp['NextContinuationToken']
        except KeyError:
            break

    return keys

def listSubfolderInFolder(prefix):
    """Get a list of all keys in an S3 bucket."""
    keys = []
    kwargs = {
        'Bucket': constants.AWS_BUCKET,
        'Prefix': prefix,
        'Delimiter':'/'
    }

    while True:
        resp = s3.list_objects_v2(**kwargs)
        
        for obj in resp.get('CommonPrefixes'):
            keys.append(obj.get('Prefix'))
            
        try:
            kwargs['ContinuationToken'] = resp['NextContinuationToken']
        except KeyError:
            break

    return keys


def copyFromS3(s3FilePath, filePath):

    s3.download_file(constants.AWS_BUCKET, s3FilePath, filePath)
