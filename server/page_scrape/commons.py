import logging
import mongoengine
import page_scrape
import boto3
import os
from botocore.exceptions import NoCredentialsError
import urllib.request

ACCESS_KEY = os.environ['ADMIN_ACCESS_KEY_ID']
SECRET_KEY = os.environ['ADMIN_SECRET_ACCESS_KEY']


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


def downloadAndSave(url, path):
    urllib.request.urlretrieve(
        url, "00000001.jpg")


def upload_to_aws(local_file, bucket, s3_file):
    s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY,
                      aws_secret_access_key=SECRET_KEY)

    try:
        s3.upload_file(local_file, bucket, s3_file)
        print("Upload Successful")
        return True
    except FileNotFoundError:
        print("The file was not found")
        return False
    except NoCredentialsError:
        print("Credentials not available")
        return False


uploaded = upload_to_aws(
    '00000001.jpg', 'sexy-girls-bucket', 'test/00000001.jpg')
