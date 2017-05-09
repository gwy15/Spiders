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

from PixivItems import *

class PixivPage():
    def __init__(self, keyword, path):
        self.keyword = keyword
        self.path = path
        # get config
        self.config = self.getConfig()
        self.headers = self.config['headers']
        logging.debug(f'__init__ get config done.')

    def getPage(self, page=1):
        logging.info(f'beginning to get page {page}')
    
        searchPageURL = self.getSearchPageURL(page, self.keyword)

        # get result page
        searchPageResponse = requests.get(searchPageURL, headers=self.headers)
        searchPage = searchPageResponse.content.decode()
        logging.debug(f'get searchPage content.')

        # get result list
        soup = bs(searchPage, 'html.parser')
        imageList = soup.find_all('li', {'class':'image-item'})

        # add to set
        picSet = set()
        albumSet = set()
        for item in imageList:
            illust_id = re.findall(r'illust_id=(\d+)', str(item))[0]
            if len(item.a['class']) == 3:
                # single
                picSet.add(illust_id)
            elif 'multiple' in item.a['class']:
                # album
                albumSet.add(illust_id)
            else:
                # unknown
                pass
        logging.debug(f'picSet: {picSet}')
        logging.debug(f'albumSet: {albumSet}')

        # get
        self.getPics(picSet)
        self.getAlbums(albumSet)

    def getPics(self, picSet):
        # for illust_id in picSet:
        #     self.getPic(illust_id)
        def func(x):
            self.getPic(x)
            time.sleep(1)
        pool = ThreadPool(5)
        pool.map(func, picSet)
        pool.close()
        pool.join()
    
    def getAlbums(self, albumSet):
        # for illust_id in albumSet:
        #    self.getAlbum(illust_id)
        def func(x):
            self.getAlbum(x)
            time.sleep(1)
        pool = ThreadPool(3)
        pool.map(func, albumSet)
        pool.close()
        pool.join()

    def getConfig(self):
        with open('config.json') as f:
            res = json.load(f)
        return res

    def getPic(self, illust_id):
        PixivSinglePic(illust_id, self.headers).getPic(self.path)

    def getAlbum(self, illust_id):
        PixivAlbum(illust_id, self.headers).getAlbum(self.path)

class PixivSearch(PixivPage):
    def getSearchPageURL(self, page, *args):
        keyword = args[0]
        keywordEncoded = urllib.parse.quote(keyword)
        searchPageURL = f'https://www.pixiv.net/search.php?word={keywordEncoded}&order=date_d&p={page}'
        logging.debug(f'search word = "{keyword}"')
        return searchPageURL

class PixivUserPage(PixivPage):
    def getSearchPageURL(self, page, *args):
        user_id = args[0]
        searchPageURL = f'https://www.pixiv.net/member_illust.php?id={user_id}&type=all&p={page}'
        return searchPageURL
