import os
import csv
import uuid
import time
import json
import random
import imghdr
import logging
import requests
import datetime
import pageScrape
import mongoengine
import coloredlogs
from PIL import Image
from time import sleep
from slugify import slugify
from sexybaby.models import Status
from bs4 import BeautifulSoup, NavigableString
from pageScrape.models import Album, ModelInfo, Tag, Category
from sexybaby import commons, aws, constants, models, cache

coloredlogs.install()
logger = logging.getLogger(__name__)

originUrl = 'https://hotgirl.biz'
source = 'hotgirlbiz'


def albumScrapeListofAlbum(pageUrl):
    """Scrape the gallery page and return list of album
    Args:
        pageUrl: Url of the pages contain all album.
    Returns:
        List of album obj
    """
    logger.info('SCRAPE ALBUM LIST IN PAGE: %s' % (pageUrl))

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
        album['albumThumbnail'] = []

        album['albumImages'] = []
        imagesHtml = html.find(
            class_='post-single-content').find(class_='thecontent').find('p').find_all('a')
        for imageHtml in imagesHtml:
            imgUrls.append(imageHtml.get('href'))

        for index in range(len(imgUrls)):
            if (index):
                try:
                    imgPath = album['albumStorePath']
                    imgExtension = imgUrls[index].split(
                        '.')[len(imgUrls[index].split('.')) - 1]
                    imgNo = format(index, '03d')
                    imgFile = imgNo + '.' + imgExtension

                    uploaded = commons.downloadAndSaveToS3(
                        imgUrls[index], imgPath, imgFile)

                    commons.debug(imgUrls[index])

                    if uploaded:
                        if imgNo == '001':
                            album['albumThumbnail'] = ['001']
                        else:
                            if len(album['albumThumbnail']) == 0:
                                album['albumThumbnail'] = [imgNo]

                            album['albumImages'].append(imgNo)
                except:
                    pass

        if len(album['albumImages']) > 5:
            Album(**album).save()
            commons.debug(album)
        else:
            logger.error('Empty images, delete album s3 storage')
            raise Exception('Empty images, delete album s3 storage')

    except:
        logger.error('Error when scraping album:' + album['albumSourceUrl'])

        if 'albumStorePath' in album:
            deleted = aws.deleteAwsS3Dir(album['albumStorePath'])
            if deleted:
                logger.info('Deleted album S3 ' + album['albumStorePath'])

    if 'albumStorePath' in album:
        commons.deleteTempPath(album['albumStorePath'])
        logger.info('Deleted album dir ' + album['albumStorePath'])


def devScrapePage():
    albumUrl = 'https://hotgirl.biz/xiaoyu-vol-304-carry/'
    albumThumbnailUrl = 'https://hotgirl.biz/wp-content/uploads/2020/06/0-24141115.jpg'

    newAlbum = {
        'albumSourceUrl': albumUrl,
        'albumThumbnail': [albumThumbnailUrl]
    }

    albumDeleteds = Album.objects(albumSourceUrl=albumUrl)
    if len(albumDeleteds) > 0:
        albumDeleted = albumDeleteds[0]
        deleted = aws.deleteAwsS3Dir(albumDeleted['albumStorePath'])
        if deleted:
            logger.info('Delete album S3 %s' %
                        (albumDeleted['albumStorePath']))
            Album.objects(albumSourceUrl=albumUrl).delete()

    else:
        albumScrapeAllImageInAlbum(newAlbum)

    # albumObjLi = albumScrapeListofAlbum('https://hotgirl.biz/')
    # print(albumObjLi)

    # for album in albumObjLi:
    #     albumScrapeAllImageInAlbum(album)


def prodPageScrape():
    pageIndex = 1
    statuses = Status.objects()
    if len(statuses) > 0:
        pageIndex = statuses[0]['hotgirlbizPage']

    for index in range(pageIndex, 364):
        pageUrl = originUrl + '/page/' + str(index)
        albumObjLi = albumScrapeListofAlbum(pageUrl)
        for album in albumObjLi:
            albumScrapeAllImageInAlbum(album)

        # Save config
        config = {
            'hotgirlbizPage': index
        }
        statuses = Status.objects()
        if len(statuses) > 0:
            status = statuses[0]
            Status.objects(id=status['id']).update_one(
                set__hotgirlbizPage=index)
        else:
            Status(**config).save()


def main():
    logger.info('Start to scrape: %s' % (source))

    if constants.DEPLOY_ENV == 'scrape':
        prodPageScrape()
    if constants.DEPLOY_ENV == 'local':
        devScrapePage()
