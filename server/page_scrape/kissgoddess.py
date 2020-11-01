
import coloredlogs
import csv
import time
import random
import requests
from bs4 import BeautifulSoup, Tag, NavigableString
from page_scrape.models import Album
import requests
import logging

originUrl = 'https://kissgoddess.com'
galleryUrl = 'https://kissgoddess.com/gallery/'
source = 'kissgoddess'

coloredlogs.install()
logging.info("It works!")


def scrapeImgInPg(url):
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
    imgUrls = []
    for imgHtml in imgLiHtml:
        imgUrl = imgHtml.get('src')
        if (imgUrl):
            imgObj = {}
            imgObj['sourceUrl'] = imgUrl
            imgUrls.append(imgObj)
    album['images'] = imgUrls

    totalPg = html.find("div", {"id": "pages"}).find_all('a')
    album['totalPg'] = len(totalPg)-1

    tagHtmls = html.find(class_='td-category').find_all('li',
                                                        {'class': 'entry-category'})
    if len(tagHtmls) > 0:
        album['tags'] = []
        for tagHtml in tagHtmls:
            tag = tagHtml.find('a').contents[0]
            if ~(tag in album['tags']):
                album['tags'].append(tag)

    album['modelName'] = html.find(
        class_='td-related-person').find(class_='td-related-peron-thumb').find('a').get('href').split('/')[2].split('.')[0]

    return album


def scrapeAllImgInAlbum(album):
    """Scrape all images in album and return list of image object
    Args:
        url(str): url of album

    Returns:
        Object of image contain title and images scraped
    """
    print('Scrape images in url:', album['url'])

    pgAlbum = scrapeImgInPg(album['url'])

    idFromSource = album['url'].split('/')[4].split('.')[0]
    if idFromSource.isnumeric():
        album['idFromSource'] = idFromSource

    album['images'] = []
    album['title'] = pgAlbum['title']
    if 'tags' in pgAlbum:
        album['tags'] = pgAlbum['tags']
    album['modelName'] = pgAlbum['modelName']

    for x in range(pgAlbum['totalPg']):
        time.sleep(0.2)

        pageUrl = album['url'].split('.html')[0] + '_' + str(x + 1) + '.html'
        pgAlbum = scrapeImgInPg(pageUrl)
        for imgObj in pgAlbum['images']:
            album['images'].append(imgObj)

    if 'thumbnail' in album:
        album['thumbnail'] = album['images'][0]

    return album


def scrapeListofAlbum():
    """Scrape the gallery page and return list of album
    Args:
        None.
    Returns:
        List of album obj
    """

    html = BeautifulSoup(requests.get(
        galleryUrl,
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


def scrapeEachGallery():
    albumObjLi = scrapeListofAlbum()

    for album in albumObjLi:
        if (album['url'] != 'https://kissgoddess.com/album/34158.html'):
            continue

        albumInDB = Album.objects(url=album['url'], source=source)

        if (len(albumInDB) == 0):

            album = scrapeAllImgInAlbum(album)
            print(album)

            album = Album(title=album['title'],
                          source=source,
                          url=album['url'],
                          tags=album['tags'],
                          modelName=album['modelName'],
                          images=album['images'],
                          thumbnail=album['thumbnail'])
            # album.save()


scrapeEachGallery()
