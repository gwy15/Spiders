import requests
import urllib
import logging
import json
import re
from bs4 import BeautifulSoup as bs
import os

logging.basicConfig(level=logging.INFO,
    format='[%(levelname)s] (%(asctime)s) %(message)s',
    datefmt='%y-%m-%d %H:%M:%S')

keyword = '1000users入り エロマンガ'
path = 'img'

class PixivItem():
    def __init__(self, headers):
        self.headers = headers
    def getPic(self, illust_id):
        logging.info(f'beginning to get illust_id {illust_id}')
        pageURL = f'https://www.pixiv.net/member_illust.php?mode=medium&illust_id={illust_id}'
        self.session = requests.Session()
        self.session.headers = self.headers
        self.session.headers['Referer'] = pageURL
        pageResponse = self.session.get(pageURL, headers=self.headers)
        pageContent = pageResponse.content.decode()
        logging.debug(f'page for {illust_id} get.')

        # soup parser
        # get title and artist
        soup = bs(pageContent, 'html.parser')
        pageTitle = soup.head.find_all('meta', {'property':"og:title"})[0]['content']
        logging.debug(f'get page title: "{pageTitle}"')
        res = re.findall(r'「([^」]+)」/「([^」]+)」\[pixiv\]', pageTitle)[0]
        self.title = res[0]
        self.artist = res[1]
        logging.info(f'title: {self.title}, artist: {self.artist}')
        
        # get pic url
        imgSoups = soup.find_all('img', {'class':"original-image"})
        if len(imgSoups) == 0:
            logging.error('no img url found. Possibly an album.')
            return
        self.oriImageURL = imgSoups[0]['data-src']
        logging.debug(f'get oriImageURL: {self.oriImageURL}')

        self.downloadImage(self.oriImageURL)
        logging.info(f'picture {illust_id} done.')

    def downloadImage(self, url):
        try:
            h = {
                'Referer':self.headers['Referer'],
                'User-Agent':self.headers['User-Agent']
            }
            response = requests.get(url, headers = h)
            if response.status_code != 200:
                logging.error(f'{response.status_code} Error')
                raise ConnectionError
        except ConnectionError as ex:
            response = self.session.get(url, headers=self.headers)
            if response.status_code == 403:
                logging.error('403 Error.')
                print(self.session.headers)
                quit()

        imageName = path + os.sep + self.title + '.' + url.split('.')[-1]
        imageName = imageName.replace('*', '※').replace('?','？')
        with open(imageName, 'wb') as f:
            f.write(response.content)

class PixivResult():
    def __init__(self):
        # get config
        self.config = self.getConfig()
        self.headers = self.config['headers']
        logging.debug(f'__init__ get config done.')

    def getPage(self, keyword, page=1):
        logging.info(f'beginning to get page {page}')

        keywordEncoded = urllib.parse.quote(keyword)
        searchPageURL = f'https://www.pixiv.net/search.php?word={keywordEncoded}&order=date_d&p={page}'
        logging.debug(f'search word = "{keyword}"')

        # get result page
        searchPageResponse = requests.get(searchPageURL, headers=self.headers)
        searchPage = searchPageResponse.content.decode()
        logging.debug(f'get searchPage content.')

        # get result list
        searchResult = re.findall('illust_id=(\d+)', searchPage)
        searchResult = list(set(searchResult))
        logging.debug(f'get searchResult: {searchResult}')

        for illust_id in searchResult:
            #get picture
            self.getPic(illust_id)

    def getConfig(self):
        with open('config.json') as f:
            res = json.load(f)
        return res

    def getPic(self, illust_id):
        PixivItem(self.headers).getPic(illust_id)

def getPixiv(keyword, page=1):
    if not os.path.exists(path):
        os.mkdir(path)
    for i in range(page):
        PixivResult().getPage(keyword, i+1)

# getPixiv(keyword, 2)
PixivResult().getPage(keyword, 3)
PixivResult().getPage(keyword, 4)
PixivResult().getPage(keyword, 5)
