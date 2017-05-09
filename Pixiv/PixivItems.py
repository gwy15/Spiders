import requests
import urllib
import logging
import json
import re
from bs4 import BeautifulSoup as bs
import os
import sys
from multiprocessing.dummy import Pool as ThreadPool
import time

class PixivItem():
    def __init__(self, illust_id, headers):
        self.illust_id = illust_id
        self.pageURL = f'https://www.pixiv.net/member_illust.php?mode=medium&illust_id={self.illust_id}'
        self.headers = headers
        self.session = requests.Session()
        self.session.headers = self.headers

    def downloadImageTo(self, url, imageName):
        if os.path.exists(imageName):
            logging.debug('img existed. skipping...')
            return
        try:
            h = {
                'Referer':self.headers['Referer'],
                'User-Agent':self.headers['User-Agent']
            }
            response = requests.get(url, headers = h)
            if response.status_code != 200:
                logging.error(f'{response.status_code} Error, retrying...')
                raise ConnectionError
        except ConnectionError as ex:
            response = self.session.get(url, headers=self.headers)
            if response.status_code == 403:
                logging.error('403 Error.')
                print(self.session.headers)
                quit()
        with open(imageName, 'wb') as f:
            f.write(response.content)

    def downloadImage(self, url, path):
        imageName = path + os.sep + self.title + ' - ' + self.artist + '.' + url.split('.')[-1]
        imageName = imageName.replace('*', '※').replace('?','？')
        self.downloadImageTo(url, imageName)

    def getTitleAndArtist(self, soup):
        # soup = bs(pageContent, 'html.parser')
        pageTitle = soup.head.find_all('meta', {'property':"og:title"})[0]['content']
        logging.debug(f'get page title: "{pageTitle}"')
        res = re.findall(r'^「(.+)」/「([^」]+)」\[pixiv\]$', pageTitle)[0]
        self.title = res[0]
        self.artist = res[1]
        def fun(x):
            if x[-1] == '.':
                x = x.replace('.', '·')
            x = re.sub(r'[\|\/]', '', x)
            x = x.replace('<', '＜').replace('>', '＞').replace(':', '：')
            x = x.replace('?', '？').replace('"', "'")
            return x
        self.title = fun(self.title)
        self.artist = fun(self.artist)

        logging.debug(f'title: "{self.title}", artist: "{self.artist}"')

    def getSoup(self, url):
        pageContent = self.getContent(url)
        soup = bs(pageContent, 'html.parser')
        return soup

    def getContent(self, url):
        try:
            pageResponse = self.session.get(url)
        except requests.exceptions.ConnectionError:
            logging.warning(f'Get content failed for url {url}. Retry in 10 seconds...')
            time.sleep(10)
            pageResponse = self.session.get(url)
        pageContent = pageResponse.content.decode()
        return pageContent

class PixivSinglePic(PixivItem):
    def __init__(self, illust_id, headers):
        PixivItem.__init__(self, illust_id, headers)
        self.session.headers['Referer'] = self.pageURL

    def getPic(self, path):
        logging.info(f'getting pic {self.illust_id}...')
        soup = self.getSoup(self.pageURL)
        logging.debug(f'page for {self.illust_id} get.')

        # get title and artist
        self.getTitleAndArtist(soup)

        # get pic url
        imgSoups = soup.find_all('img', {'class':"original-image"})
        if len(imgSoups) == 0:
            logging.error('no img url found.')
            return
        self.oriImageURL = imgSoups[0]['data-src']
        logging.debug(f'get oriImageURL: {self.oriImageURL}')

        # download
        self.downloadImage(self.oriImageURL, path)
        logging.info(f'picture {self.title} - {self.artist} ({self.illust_id}) done.')

class PixivAlbum(PixivItem):
    def __init__(self, illust_id, headers):
        PixivItem.__init__(self, illust_id, headers)
        self.albumURL = f'https://www.pixiv.net/member_illust.php?mode=manga&illust_id={illust_id}'
        self.session.headers['Referer'] = self.albumURL
    
    def getAlbum(self, path):
        logging.info(f'getting album {self.illust_id}...')
        
        # get title
        soup = self.getSoup(self.pageURL)
        logging.debug(f'page for {self.illust_id} (main page) get.')
        self.getTitleAndArtist(soup)
        
        # get pic urls
        picURLs = set()
        soup = self.getSoup(self.albumURL)
        imageContainers = soup.find_all('div', {'class':'item-container'})
        for item in imageContainers:
            picURLs.add(item.img['data-src'])
        
        # mkdir
        thisPath = path + os.sep + self.title + ' - ' + self.artist
        if not os.path.exists(thisPath):
            os.mkdir(thisPath)

        self.count = 1
        def func(url):
            self.downloadImage(url, path)
            logging.debug(f'({self.title} - {self.artist}) pic {self.count} done.')
            self.count += 1
        pool = ThreadPool(5)
        pool.map(func, picURLs)
        pool.close()
        pool.join()

        logging.info(f'album {self.title} - {self.artist} ({self.illust_id}) done.')

    def downloadImage(self, url, path):
        thisPath = path + os.sep + self.title + ' - ' + self.artist

        num = re.findall(r'p(\d+)', url)[0]
        imageName = thisPath + os.sep + num + '.' + url.split('.')[-1]
        imageName = imageName.replace('*', '※').replace('?','？')
        self.downloadImageTo(url, imageName)

def _main():
    pass

if __name__ == '__main__':
    _main()
