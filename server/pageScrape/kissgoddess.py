
import coloredlogs
import csv
import uuid
import time
import random
import requests
from bs4 import BeautifulSoup, Tag, NavigableString
from pageScrape.models import Album
import requests
import logging
import mongoengine
import pageScrape
from slugify import slugify
from pageScrape.commons import dataLogging, downloadAndSave, uploadToAws, deleteTempPath, getAlbumId, getImgId, deleteAwsS3Dir, debug

originUrl = 'https://kissgoddess.com'
source = 'kissgoddess'

coloredlogs.install()


def scrapeListofAlbum(listUrl):
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
            thnailUrl = albumHtml.find(
                'img', {'class': 'entry-thumb'}).get('data-original')

            if (albumUrl):
                album = {
                    'albumSourceUrl': albumUrl,
                    'albumThumbnail': {
                        'imgSourceUrl': thnailUrl
                    }
                }

                albumLi.append(album)

    return albumLi


def scrapeImgInPg(url, albumId):
    """Scrape all images inside the url of album and return list of image object
    Args:
        url (str): url of album

    Returns:
        Object of image contain title and images scraped
    """

    html = BeautifulSoup(requests.get(
        url,
        verify=True).text, 'html.parser')

    album = {}
    album['albumDisplayTitle'] = html.find(
        class_='td-post-header').find(class_='td-post-title').find(class_='entry-title').contents[0]

    imgLiHtml = html.find(class_='td-gallery-content').find_all('img')
    imgObjs = []
    for imgHtml in imgLiHtml:
        imgUrl = imgHtml.get('src')
        if imgUrl and (len(albumId) > 0):
            imgPath = 'album/' + albumId
            imgFile = getImgId() + '.' + \
                imgUrl.split('.')[len(imgUrl.split('.')) - 1]

            uploaded = downloadAndSave(
                imgUrl, imgPath, imgFile)

            if uploaded:
                imgObj = {}
                imgObj['imgSourceUrl'] = imgUrl
                imgObj['imgStorePath'] = imgPath + '/' + imgFile
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

    album['modelName'] = html.find(
        class_='td-related-person').find(class_='td-related-peron-thumb').find('a').get('href').split('/')[2].split('.')[0]
    album['modelDisplayName'] = html.find(
        class_='td-related-person').find(class_='td-related-peron-thumb').find('a').get('title')

    return album


def scrapeAllImgInAlbum(album):
    """Scrape all images in album and return list of image object
    Args:
        url(str): url of album

    Returns:
        Object of image contain title and images scraped
    """
    debug('Scrape images in url: %s' % (album['albumSourceUrl']))

    pgAlbum = scrapeImgInPg(album['albumSourceUrl'], '')

    idFromSource = album['albumSourceUrl'].split('/')[4].split('.')[0]
    if idFromSource.isnumeric():
        album['albumIdFromSource'] = idFromSource

    album['albumId'] = getAlbumId()
    album['albumImages'] = []
    album['albumDisplayTitle'] = pgAlbum['albumDisplayTitle']
    album['albumTitle'] = slugify(
        pgAlbum['albumDisplayTitle'], to_lower=True)

    if 'albumTags' in pgAlbum:
        album['albumTags'] = pgAlbum['albumTags']
    album['modelName'] = pgAlbum['modelName']
    album['modelDisplayName'] = pgAlbum['modelDisplayName']

    for x in range(pgAlbum['totalPg']):
        time.sleep(0.2)

        pageUrl = album['albumSourceUrl'].split(
            '.html')[0] + '_' + str(x + 1) + '.html'
        pgAlbum = scrapeImgInPg(pageUrl, album['albumId'])
        for imgObj in pgAlbum['albumImages']:
            imgObj['imgNo'] = len(album['albumImages']) + 1
            album['albumImages'].append(imgObj)

    if (not 'albumThumbnail' in album):
        if (len(album['albumImages']) > 0):
            album['albumThumbnail'] = album['albumImages'][0]
        else:
            album['albumThumbnail'] = {}

    deleteTempPath('album/' + album['albumId'])

    return album


def scrapeEachAlbum(album):
    """Scrape, save all images of album to S3 and Mongo DB
    Args:
        album (dict)
    Returns:
        None
    """
    albumInDB = Album.objects(
        albumSourceUrl=album['albumSourceUrl'], albumSource=source)

    if (len(albumInDB) == 0):

        album = scrapeAllImgInAlbum(album)
        debug(album)
        try:
            album = Album(albumTitle=album['albumTitle'],
                          albumDisplayTitle=album['albumDisplayTitle'],
                          albumSource=source,
                          albumSourceUrl=album['albumSourceUrl'],
                          albumIdFromSource=album['albumIdFromSource'],
                          albumTags=album['albumTags'],
                          albumId=album['albumId'],
                          modelName=album['modelName'],
                          modelDisplayName=album['modelDisplayName'],
                          albumImages=album['albumImages'],
                          albumThumbnail=album['albumThumbnail'])

            album.save()
        except:
            debug('Delete album ' + album['albumId'])
            deleteAwsS3Dir('album/' + album['albumId'])

    else:
        dataLogging(albumInDB[0], '')


def scrapeEachGallery():
    listUrl = originUrl + '/gallery/'
    albumObjLi = scrapeListofAlbum(listUrl)

    for album in albumObjLi:
        if (album['albumSourceUrl'] != 'https://kissgoddess.com/album/34143.html'):
            continue

        scrapeEachAlbum(album)


def main():
    logging.info('Start to scrape: %s' % (source))

    scrapeEachAlbum({
        'albumSourceUrl': 'https://kissgoddess.com/album/34171.html'
    })
    # scrapeEachGallery()
