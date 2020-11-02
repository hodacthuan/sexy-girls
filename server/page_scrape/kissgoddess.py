
import coloredlogs
import csv
import uuid
import time
import random
import requests
from bs4 import BeautifulSoup, Tag, NavigableString
from page_scrape.models import Album
import requests
import logging
import mongoengine
import page_scrape
from page_scrape.commons import dataLogging, downloadAndSave, uploadToAws, deleteTempPath, getAlbumId, getImgId

originUrl = 'https://kissgoddess.com'
galleryUrl = 'https://kissgoddess.com/gallery/'
source = 'kissgoddess'

coloredlogs.install()
logging.info("It works!")


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
                    'url': albumUrl,
                    'thumbnail': {
                        'sourceUrl': thnailUrl
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
    album['title'] = html.find(
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
                imgObj['sourceUrl'] = imgUrl
                imgObj['storePath'] = imgPath + '/' + imgFile
                imgObjs.append(imgObj)

    album['images'] = imgObjs

    totalPg = html.find("div", {"id": "pages"}).find_all('a')
    album['totalPg'] = len(totalPg)-1

    tagHtmls = html.find(class_='td-category').find_all('li',
                                                        {'class': 'entry-category'})
    if len(tagHtmls) > 0:
        album['tags'] = []
        for tagHtml in tagHtmls:
            tag = tagHtml.find('a').contents[0]
            if not(tag in album['tags']):
                album['tags'].append(tag)

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
    print('Scrape images in url:', album['url'])

    pgAlbum = scrapeImgInPg(album['url'], '')

    idFromSource = album['url'].split('/')[4].split('.')[0]
    if idFromSource.isnumeric():
        album['idFromSource'] = idFromSource

    album['albumId'] = getAlbumId()
    album['images'] = []
    album['title'] = pgAlbum['title']
    if 'tags' in pgAlbum:
        album['tags'] = pgAlbum['tags']
    album['modelName'] = pgAlbum['modelName']
    album['modelDisplayName'] = pgAlbum['modelDisplayName']

    for x in range(pgAlbum['totalPg']):
        time.sleep(0.2)

        pageUrl = album['url'].split('.html')[0] + '_' + str(x + 1) + '.html'
        pgAlbum = scrapeImgInPg(pageUrl, album['albumId'])
        for imgObj in pgAlbum['images']:
            album['images'].append(imgObj)

    if (not 'thumbnail' in album):
        if (len(album['images']) > 0):
            album['thumbnail'] = album['images'][0]
        else:
            album['thumbnail'] = {}

    deleteTempPath('album/' + album['albumId'])

    return album


def scrapeEachAlbum(album):
    print(type(album))
    """Scrape, save all images of album to S3 and Mongo DB
    Args:
        album (dict)
    Returns:
        None
    """
    albumInDB = Album.objects(url=album['url'], source=source)

    if (len(albumInDB) == 0):

        album = scrapeAllImgInAlbum(album)
        print(album)

        album = Album(title=album['title'],
                      source=source,
                      url=album['url'],
                      idFromSource=album['idFromSource'],
                      tags=album['tags'],
                      albumId=album['albumId'],
                      modelName=album['modelName'],
                      modelDisplayName=album['modelDisplayName'],
                      images=album['images'],
                      thumbnail=album['thumbnail'])
        print(album)
        album.save()
    else:
        dataLogging(albumInDB[0], '')


def scrapeEachGallery():
    listUrl = originUrl + '/gallery/'
    albumObjLi = scrapeListofAlbum(listUrl)

    for album in albumObjLi:
        if (album['url'] != 'https://kissgoddess.com/album/34143.html'):
            continue

        scrapeEachAlbum(album)


scrapeEachAlbum({
    'url': 'https://kissgoddess.com/album/34025.html'
})
# scrapeEachGallery()
