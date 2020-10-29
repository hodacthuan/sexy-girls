
import csv, time,random,requests
from bs4 import BeautifulSoup
from page_scrape.models import Post
import requests
# https://www.digitalocean.com/community/tutorials/how-to-scrape-web-pages-with-beautiful-soup-and-python-3

originUrl = "https://www.xsnvshen.com/"
mainUrl = "https://www.xsnvshen.com/album/"
source='xsnvshen'


def scrapeEachPost(url,thumbnail):
    postFoundInDB = Post.objects(url=url,source=source)
    if ~(len(postFoundInDB)==0): 
        time.sleep(2)
        html = BeautifulSoup(requests.get(url, verify = False).text, 'html.parser')
        title = html.find("img", {"id": "bigImg"}).get('alt')
        
        print('Scrape post:',title)
        firstImageUrl = html.find("img", {"id": "bigImg"}).get('src').replace('//','https://')
        imageUrl = firstImageUrl.split('/000.')
        bot = 0
        top = 100
        while ((top-bot)>1):
            num = int((top+bot)/2)
            numStr =('0000' +str(num))[-3:]
           
            indexUrl= imageUrl[0]+'/'+numStr+'.'+imageUrl[1]
            print(indexUrl)
            if (requests.get(indexUrl).status_code==200):
                bot = num
            else:
                top = num
        
        
        
        print(bot)
        # images=[]
        # for paginationUrl in paginationUrlList:
        #     print('Scrape page:',paginationUrl)
        #     time.sleep(1)
        #     html = BeautifulSoup(requests.get(paginationUrl).text, 'html.parser')
        #     imagesHtmlList = html.find(class_='post-inner').find(class_='entry').find('p').find_all('img')
            
        #     for imageHtml in imagesHtmlList:
        #         imagelink =  imageHtml.get('src');
        #         images.append({"sourceUrl":imagelink,"publish":False})
       
        # print('Total images',len(images))
        # post = Post(title=title, source=source, url=url,images=images,thumbnail=thumbnail )
        # post.save()
    


def scrapeMainPage():
    html = BeautifulSoup(requests.get(mainUrl, verify = False ).text, 'html.parser')
  
    postHtmlList = html.find(class_='index_listc').find(class_='pos_6_1').find('ul').find_all('li')
  
    for postHtml in postHtmlList:
        postUrl =mainUrl+ postHtml.find('a').get('href').split('/')[2]

        thumbnail = postHtml.find('a').find('img').get('src').replace('//','https://')
     
        if postUrl :
            scrapeEachPost(postUrl,thumbnail)

scrapeMainPage()

