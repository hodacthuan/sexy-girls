
import csv, time,random,requests
from bs4 import BeautifulSoup
from page_scrape.models import Post
# https://www.digitalocean.com/community/tutorials/how-to-scrape-web-pages-with-beautiful-soup-and-python-3


mainUrl = "https://mrcong.com/"
source='mrcong'


def scrapeEachPost(url,thumbnail):
    postFoundInDB = Post.objects(url=url,source=source)
    if ~(len(postFoundInDB)==0): 
        time.sleep(5)
        html = BeautifulSoup(requests.get(url).text, 'html.parser')
        title = html.find(class_='post-title').find('span').contents[0].split('(')[0]
        
        print('Scrape post:',title)
        paginationHtml = html.find(class_='post-inner').find(class_='entry').find(class_='page-link').find_all('a')
        paginationUrlList =[]
        paginationUrlList.append(url)
        for pagination in paginationHtml:
            paginationUrl =  pagination.get('href');
            paginationUrlList.append(paginationUrl)
        # print(paginationUrlList)
        images=[]
        for paginationUrl in paginationUrlList:
            print('Scrape page:',paginationUrl)
            time.sleep(1)
            html = BeautifulSoup(requests.get(paginationUrl).text, 'html.parser')
            imagesHtmlList = html.find(class_='post-inner').find(class_='entry').find('p').find_all('img')
            
            for imageHtml in imagesHtmlList:
                imagelink =  imageHtml.get('src');
                images.append({"sourceUrl":imagelink,"publish":False})
       
        print('Total images',len(images))
        post = Post(title=title, source=source, url=url,images=images,thumbnail=thumbnail )
        post.save()
    


def scrapeMainPage():
    html = BeautifulSoup(requests.get(mainUrl).text, 'html.parser')
    # last_links.decompose()
    postHtmlList = html.find(class_='post-listing').find_all('article')
    for postHtml in postHtmlList:
        postUrl =  postHtml.find(class_='post-thumbnail').find('a').get('href')
        thumbnail = postHtml.find(class_='post-thumbnail').find('a').find('img').get('src')
        if postUrl :
            scrapeEachPost(postUrl,thumbnail)

# scrapeMainPage()




# for i in range(1, 5):
#     url = 'https://web.archive.org/web/20121007172955/https://www.nga.gov/collection/anZ' + str(i) + '.htm'
#     pages.append(url)

