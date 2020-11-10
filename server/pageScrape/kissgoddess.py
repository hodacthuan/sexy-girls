
import coloredlogs
import csv
import uuid
import os
import time
import random
import json
import imghdr
from PIL import Image
import requests
from bs4 import BeautifulSoup, Tag, NavigableString
from pageScrape.models import Album, ModelInfo
import requests
import logging
import mongoengine
import pageScrape
from slugify import slugify
from sexybaby.commons import dataLogging, downloadAndSaveToS3, deleteTempPath, getLongId, getShortId, debug
from sexybaby.aws import deleteAwsS3Dir, uploadToAws
import logging
logger = logging.getLogger(__name__)

originUrl = 'https://kissgoddess.com'
source = 'kissgoddess'

coloredlogs.install()


def albumScrapeListofAlbum(listUrl):
    """Scrape the gallery page and return list of album
    Args:
        None.
    Returns:
        List of album obj
    """

    html = BeautifulSoup(requests.get(
        listUrl,
        verify=True
    ).text, 'html.parser')

    albumLiHtml = html.find_all(class_='td-related-gallery')

    albumLi = []
    for albumHtml in albumLiHtml:
        if isinstance(albumHtml.find('a'), Tag):
            albumUrl = originUrl + albumHtml.find('a').get('href')

            if (albumUrl):
                album = {
                    'albumSourceUrl': albumUrl,
                }

                albumLi.append(album)

    return albumLi


def albumScrapeImageInPage(url, albumId):
    """Scrape all images inside the url of album and return list of image object
    Args:
        url (str): url of album

    Returns:
        Object of image contain title and images scraped
    """

    html = BeautifulSoup(requests.get(
        url,
        verify=True).text, 'html.parser')

    album = dict()
    album['albumDisplayTitle'] = html.find(
        class_='td-post-header').find(class_='td-post-title').find(class_='entry-title').contents[0]

    imgLiHtml = html.find(class_='td-gallery-content').find_all('img')
    imgObjs = []
    for imgHtml in imgLiHtml:
        imgUrl = imgHtml.get('src')
        if imgUrl and (albumId is not None):
            imgPath = 'album/' + albumId
            imgExtension = imgUrl.split('.')[len(imgUrl.split('.')) - 1]
            imgFile = getShortId() + '.' + imgExtension
            imgTempFilePath = '/tmp/' + imgPath + '/' + imgFile

            uploaded = downloadAndSaveToS3(
                imgUrl, imgPath, imgFile)

            imgOpened = Image.open(imgTempFilePath)

            if uploaded:
                imgObj = {}
                imgObj['imgWidth'] = imgOpened.size[0]
                imgObj['imgHeight'] = imgOpened.size[1]
                imgObj['imgSize'] = os.path.getsize(imgTempFilePath)
                imgObj['imgType'] = imghdr.what(imgTempFilePath)
                imgObj['imgSourceUrl'] = imgUrl
                imgObj['imgStorePath'] = imgPath + '/' + imgFile
                imgObj['imgExtension'] = imgExtension
                imgObjs.append(imgObj)

    album['albumImages'] = imgObjs

    totalPg = html.find("div", {"id": "pages"}).find_all('a')
    album['totalPg'] = len(totalPg)-1

    tagHtmls = html.find(class_='td-category').find_all('li',
                                                        {'class': 'entry-category'})
    if len(tagHtmls) > 0:
        album['albumTags'] = []
        for tagHtml in tagHtmls:
            tag = tagHtml.find('a').contents[0]
            if not(tag in album['albumTags']):
                album['albumTags'].append(tag)

    album['albumModelName'] = html.find(
        class_='td-related-person').find(class_='td-related-peron-thumb').find('a').get('href').split('/')[2].split('.')[0]

    return album


def albumScrapeAllImageInAlbum(albumUrl):
    """Scrape all images in album and return list of image object
    Args:
        url(str): url of album

    Returns:
        Object of image contain title and images scraped
    """
    albumInDB = Album.objects(
        albumSourceUrl=albumUrl, albumSource=source)

    if not (len(albumInDB) == 0):
        dataLogging(albumInDB[0], '')
        return

    album = dict()
    album['albumSourceUrl'] = albumUrl
    debug('Scrape images in url: %s' % (album['albumSourceUrl']))

    pgAlbum = albumScrapeImageInPage(album['albumSourceUrl'], None)

    album['albumSource'] = source

    idFromSource = album['albumSourceUrl'].split('/')[4].split('.')[0]
    if idFromSource.isnumeric():
        album['albumIdFromSource'] = idFromSource

    album['albumId'] = getLongId()
    album['albumImages'] = []
    album['albumDisplayTitle'] = pgAlbum['albumDisplayTitle']
    album['albumTitle'] = slugify(
        pgAlbum['albumDisplayTitle'], to_lower=True)

    if 'albumTags' in pgAlbum:
        album['albumTags'] = pgAlbum['albumTags']
    album['albumModelName'] = pgAlbum['albumModelName']

    for x in range(pgAlbum['totalPg']):
        time.sleep(0.2)

        pageUrl = album['albumSourceUrl'].split(
            '.html')[0] + '_' + str(x + 1) + '.html'
        pgAlbum = albumScrapeImageInPage(pageUrl, album['albumId'])
        for imgObj in pgAlbum['albumImages']:
            imgObj['imgNo'] = format(len(album['albumImages']) + 1, '03d')
            album['albumImages'].append(imgObj)

    if (not 'albumThumbnail' in album):
        if (len(album['albumImages']) > 0):
            album['albumThumbnail'] = album['albumImages'][0]
        else:
            album['albumThumbnail'] = {}

    deleteTempPath('album/' + album['albumId'])

    try:
        Album(**album).save()

    except:
        logger.error('Cannot save to DB:' + album['albumSourceUrl'])
        debug('Delete album ' + album['albumId'])
        deleteAwsS3Dir('album/' + album['albumId'])


def modelScrapeAllModelsInfo(modelUrl):
    """Scrape, save all info of model to S3 and Mongo DB
    Args:
        modelsUrl
    Returns:
        None
    """

    modelInDB = ModelInfo.objects(
        modelSourceUrl=modelUrl, modelSource=source)

    if not (len(modelInDB) == 0):
        dataLogging(modelInDB[0], '')
        return

    html = BeautifulSoup(requests.get(
        modelUrl,
        verify=True).text, 'html.parser')
    # print(html)
    model = {}
    model['modelSourceUrl'] = modelUrl
    model['modelIsPublic'] = False
    model['modelSource'] = source
    model['modelName'] = modelUrl.split(
        '/')[len(modelUrl.split('/'))-1].split('.')[0]
    model['modelDisplayName'] = html.find(
        class_='person-name').contents[0]

    model['modelProfession'] = html.find(
        class_='person-profession').contents[0]

    articles = html.find('article"')

    model['modelAbout'] = []
    for article in articles:
        if (article.find(class_='td-pulldown-size')):
            title = article.find(class_='td-pulldown-size').contents[0]

            if title == 'Height & Measurements':
                model['modelHeightMeasurements'] = article.find(
                    'p').contents[0]

            if title == 'About':
                about = article.find('p').find('p').contents[0]
                model['modelAbout'].append(about)

            if title == 'Before Fame':
                about = article.find('p').contents[0]
                model['modelAbout'].append(about)

    model['modelImage'] = dict()
    model['modelImage']['imgSourceUrl'] = html.find(
        class_='td-post-content').find(
        class_='td-post-featured-image').find('a').get('href')
    model['modelImage']['imgIsPublic'] = False

    personalInfos = html.find(class_='person-pro')

    for personalInfo in personalInfos:
        title = personalInfo.find('h6').contents[0]

        if title == 'BIRTHDAY':
            model['modelBirthday'] = personalInfo.find(
                'span').contents[0]

        if title == 'BIRTHPLACE':
            model['modelBirthPlace'] = personalInfo.find(
                'span').contents[0]
        if title == 'AGE':
            model['modelAge'] = personalInfo.find(
                'span').contents[0]
        if title == 'BIRTH SIGN':
            model['modelSign'] = personalInfo.find(
                'span').contents[0]
        if title == 'HOBBY':
            model['modelHobbies'] = []
            model['modelHobbies'].append(personalInfo.find(
                'span').contents[0])

    modelId = getLongId()
    imgUrl = model['modelImage']['imgSourceUrl']
    imgPath = 'model/' + modelId
    imgExtension = imgUrl.split('.')[len(imgUrl.split('.')) - 1]
    imgFile = getShortId() + '.' + imgExtension
    imgTempFilePath = '/tmp/' + imgPath + '/' + imgFile

    uploaded = downloadAndSaveToS3(
        imgUrl, imgPath, imgFile)

    imgOpened = Image.open(imgTempFilePath)

    if uploaded:
        model['modelImage']['imgNo'] = '001'
        model['modelImage']['imgWidth'] = imgOpened.size[0]
        model['modelImage']['imgHeight'] = imgOpened.size[1]
        model['modelImage']['imgSize'] = os.path.getsize(imgTempFilePath)
        model['modelImage']['imgType'] = imghdr.what(imgTempFilePath)
        model['modelImage']['imgSourceUrl'] = imgUrl
        model['modelImage']['imgStorePath'] = imgPath + '/' + imgFile
        model['modelImage']['imgExtension'] = imgExtension

    print(model)
    try:
        ModelInfo(**model).save()

    except (RuntimeError, TypeError, NameError):
        logger.error('Cannot save to DB:')


def scrapeEachGallery():
    listUrl = originUrl + '/gallery/'
    albumObjLi = albumScrapeListofAlbum(listUrl)

    for album in albumObjLi:
        if (album['albumSourceUrl'] != 'https://kissgoddess.com/album/34143.html'):
            continue

        albumScrapeAllImageInAlbum(album)


def main():
    logging.info('Start to scrape: %s' % (source))

    albumScrapeAllImageInAlbum('https://kissgoddess.com/album/34171.html')
    modelScrapeAllModelsInfo('https://kissgoddess.com/people/xie-zhi-xin.html')
    # scrapeEachGallery()
