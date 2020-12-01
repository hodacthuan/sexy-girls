import os
import time
import uuid
import boto3
import shutil
import logging
import botocore
import pageScrape
import mongoengine
import coloredlogs
from sexybaby.constants import *
from botocore.exceptions import NoCredentialsError
from botocore.errorfactory import ClientError
import urllib.request
coloredlogs.install()

s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY,
                  aws_secret_access_key=AWS_SECRET_KEY)


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
            Bucket=AWS_BUCKET,
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
        s3.upload_file(filePath, AWS_BUCKET, s3FilePath, ExtraArgs={
                       'ContentType': 'image/jpeg'})
        return True
    except FileNotFoundError:
        print("The file was not found", filePath)
        return False
    except NoCredentialsError:
        print("Credentials not available")
        return False


def getObjectSize(s3FilePath):

    try:
        response = s3.head_object(
            Bucket=AWS_BUCKET,
            Key=s3FilePath)
        size = response['ContentLength']
        return size
    except FileNotFoundError:
        print("The file was not found", s3FilePath)
        return False
    except NoCredentialsError:
        print("Credentials not available")
        return False


def listAllObjectsInFolder(prefix):
    """Get a list of all keys in an S3 bucket."""
    keys = []
    try:
        kwargs = {
            'Bucket': AWS_BUCKET,
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
    except:
        return keys


def listSubfolderInFolder(prefix):
    """Get a list of all keys in an S3 bucket."""
    keys = []
    kwargs = {
        'Bucket': AWS_BUCKET,
        'Prefix': prefix,
        'Delimiter': '/'
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


def copyObjectByKey(fromKey, toKey):

    copySource = {
        'Bucket': AWS_BUCKET,
        'Key': fromKey
    }
    s3.copy(copySource, AWS_BUCKET, toKey)

    return True


def copyFromS3(s3FilePath, filePath):
    try:
        s3.download_file(AWS_BUCKET, s3FilePath, filePath)
    except:
        pass


def ifKeyExist(key):
    try:
        s3.head_object(Bucket=AWS_BUCKET, Key=key)

    except ClientError:
        return False

    return True
