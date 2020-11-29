import json
import redis
from . import constants
from django.core import serializers
from pageScrape.models import Album, Category, Tag
from django.forms.models import model_to_dict

pool = redis.ConnectionPool(
    host=constants.REDISDB_SERVER,
    port=constants.REDISDB_PORT,
    db=constants.REDISDB_DBNUMBER,
    password=constants.REDISDB_PASSWORD
)

redisClient = redis.Redis(connection_pool=pool)

ttl = {
    'month': 86400*30,
    'week': 86400*7,
    'day': 86400,
    'h6': 21600,
    'm10': 600,
    'h1': 3600,
    'h3': 10800
}

typeKey = {
    'request': 'request:',
    'response': 'response:',
    'database': 'database:',
    'storage': 'storage:',
    'ip': 'ip:',
}

modelKey = {
    'album': 'album:',
    'tag': 'tag:',
    'category': 'category:',
}


sourceKey = {
    'hotgirlbiz': 'hotgirlbiz:',
    'kissgoddess': 'kissgoddess:',

}

functionKey = {
    'copyAlbumImagesFromS3ToServer': 'copyAlbumImagesFromS3ToServer:',
    'copyAlbumThumbnailFromS3ToServer': 'copyAlbumThumbnailFromS3ToServer:',
    'listByTag': 'listByTag:',
    'getAlbumDetailByTitle': 'getAlbumDetailByTitle:',
    'getTagDetailByTitle': 'getTagDetailByTitle:',
}


def envKey(key):
    return constants.DEPLOY_ENV + ':' + key


def get(key):
    result = redisClient.get(envKey(key))
    if result:
        return result.decode('utf-8')
    else:
        return None


def set(key, value):
    return redisClient.set(envKey(key), value.encode('utf-8'))


def setex(key, value, ttl):
    return redisClient.set(envKey(key), value.encode('utf-8'), ttl)
