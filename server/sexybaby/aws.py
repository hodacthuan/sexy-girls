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


def copyFromS3(s3FilePath, filePath):

    s3.download_file(constants.AWS_BUCKET, s3FilePath, filePath)
