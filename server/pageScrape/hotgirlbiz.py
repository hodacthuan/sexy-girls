
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


def albumScrapeListofAlbum(pageUrl):
    """Scrape the gallery page and return list of album
    Args:
        pageUrl: Url of the pages contain all album.
    Returns:
        List of album obj
    """
    logger.info('Scrape album list in url: %s' % (pageUrl))

    html = BeautifulSoup(requests.get(
        pageUrl,
        verify=True
    ).text, 'html.parser')

    albumLiHtml = html.find_all(class_='latestPost')

    albumLi = []
    for albumHtml in albumLiHtml:

        albumUrl = albumHtml.find('a').get('href')
        imageUrl = albumHtml.find_all(
            class_='featured-thumbnail')[0].find('img').get('data-lazy-src')
        displayTitle = albumHtml.find_all(
            class_='featured-thumbnail')[0].find('img').get('alt')
        title = slugify(displayTitle, to_lower=True)

        if (albumUrl and imageUrl):
            album = {
                'albumSourceUrl': albumUrl,
                'albumThumbnail': [imageUrl],
                'albumDisplayTitle': displayTitle,
                'albumTitle': title,
            }

            albumLi.append(album)

    return albumLi


def albumScrapeAllImageInAlbum(album):
    """Scrape all images in album and return list of image object
    Args:
        album: album

    Returns:
        Object of image contain title and images scraped
    """
    if 'albumTitle' in album:
        albumInDB = Album.objects(albumTitle=album['albumTitle'])
    else:
        logger.info('Find album by url: %s' % (album['albumSourceUrl']))
        albumInDB = Album.objects(
            albumSourceUrl=album['albumSourceUrl'])

    if not (len(albumInDB) == 0):
        logger.info('Album existing in DB: %s' % (album['albumSourceUrl']))
        return

    logger.info('Scrape images in album: %s' % (album['albumSourceUrl']))

    try:
        html = BeautifulSoup(requests.get(
            album['albumSourceUrl'],
            verify=True).text, 'html.parser')

        album['albumSource'] = source

        album['albumDisplayTitle'] = html.find(
            class_='single_post').find(class_='single-title').contents[0]

        album['albumTitle'] = slugify(
            album['albumDisplayTitle'], to_lower=True)

        album['albumUpdatedDate'] = html.find(
            class_='single_post').find(class_='thetime').find('span').contents[0]

        dateFormatted = datetime.datetime.strptime(
            album['albumUpdatedDate'], "%B %d, %Y").strftime("%Y-%m-%d")
        if len(dateFormatted) != 10:
            return
        date = str(dateFormatted).split(' ')[0].split('-')
        album['albumStorePath'] = 'album/' + date[0] + '-' + date[1] + \
            '/' + date[2] + '/' + commons.getShortId()

        album['albumTags'] = []
        tagsHtml = html.find(
            class_='single_post').find(class_='tags').find_all('a')
        for tagHtml in tagsHtml:
            album['albumTags'].append(commons.getTagTitle(tagHtml.contents[0]))

        album['albumCategories'] = []
        categoriesText = html.find(
            class_='single_post').find(class_='thecategory').contents[0]
        categories = categoriesText.split(',')
        for category in categories:
            album['albumCategories'].append(commons.getCategoryTitle(category))

        imgUrls = []
        imgUrls.append(album['albumThumbnail'][0])

        album['albumImages'] = []
        imagesHtml = html.find(
            class_='post-single-content').find(class_='thecontent').find('p').find_all('a')
        for imageHtml in imagesHtml:
            imgUrls.append(imageHtml.get('href'))

        for index in range(len(imgUrls)):
            if (index):
                imgPath = album['albumStorePath']
                imgExtension = imgUrls[index].split(
                    '.')[len(imgUrls[index].split('.')) - 1]
                imgNo = format(index, '03d')
                imgFile = imgNo + '.' + imgExtension

                uploaded = downloadAndSaveToS3(
                    imgUrls[index], imgPath, imgFile)

                if uploaded:
                    if imgNo == '001':
                        album['albumThumbnail'] = ['001']
                    else:
                        album['albumImages'].append(imgNo)

        Album(**album).save()

    except:
        logger.error('Cannot save to DB:' + album['albumSourceUrl'])
        debug('Delete album ' + album['albumSourceUrl'])
        if 'albumStorePath' in album:
            deleteAwsS3Dir(album['albumStorePath'])

    # logger.info(album)
    if 'albumStorePath' in album:
        deleteTempPath(album['albumStorePath'])


def devScrapePage():
    albumUrl = 'https://hotgirl.biz/xiuren-vol-2525-jiu-shi-a-zhu/'

    newAlbum = {
        'albumSourceUrl': albumUrl,
        'albumThumbnail': ['https://cdn.besthotgirl.com/assets/uploads/224416.jpg']
    }

    albumDeleteds = Album.objects(albumSourceUrl=albumUrl)
    if len(albumDeleteds) > 0:
        albumDeleted = albumDeleteds[0]
        oldStorePath = albumDeleted['albumStorePath']
        deleted = aws.deleteAwsS3Dir(oldStorePath)
        if deleted:
            Album.objects(albumSourceUrl=albumUrl).delete()
            logger.info('Delete album : %s' %
                        (albumDeleted['albumSourceUrl']))

    else:
        albumScrapeAllImageInAlbum(newAlbum)

    # albumObjLi = albumScrapeListofAlbum('https://hotgirl.biz/')
    # print(albumObjLi)

    # for album in albumObjLi:
    #     albumScrapeAllImageInAlbum(album)


def main():
    logger.info('Start to scrape: %s' % (source))

    if constants.DEPLOY_ENV == 'scrape':

        for index in range(364):
            pageUrl = originUrl + '/page/' + str(index + 1)
            albumObjLi = albumScrapeListofAlbum(pageUrl)
            for album in albumObjLi:
                albumScrapeAllImageInAlbum(album)

    if constants.DEPLOY_ENV == 'local':
        devScrapePage()
