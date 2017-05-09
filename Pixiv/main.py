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
from PixivPages import *

path = 'img'

def createIfNotExists(path):
    if not os.path.exists(path):
        os.mkdir(path)

def getPixivSearch(keyword, page=1):
    logging.info(f'starting to get pixiv (keyword = "{keyword}", page={page})')
    createIfNotExists(path)

    search = PixivSearch(keyword, path)
    for i in range(page):
        search.getPage(i+1)

def doPixivSearch():
    keywords = input('Input search words: ')
    page = int(input('search page count: '))
    getPixivSearch(keywords, page)

def getPixivUser(user_id, page=1):
    logging.info(f'starting to get user (user_id = {user_id}, page={page})')
    createIfNotExists(path)

    user = PixivUserPage(user_id, path)
    for i in range(page):
        user.getPage(i+1)

def doPixivUser():
    user_id = input('Input user id: ')
    page = int(input('Input page count: '))
    getPixivUser(user_id, page)

def init():
    loggingLevel = logging.INFO
    for item in sys.argv[1:]:
        if item.upper() in ('-D', '-DEBUG'):
            loggingLevel = logging.DEBUG
    logging.basicConfig(level=loggingLevel,
        format='(%(asctime)s) - [%(levelname)s] %(message)s',
        datefmt='%y-%m-%d %H:%M:%S')

def doChoice():
    print('1. Search certain keywords and download the result page.')
    print('2. For a certain user, download his or her picures.')
    choose = input('input choose: ')
    if '1' in choose:
        doPixivSearch()
    elif '2' in choose:
        doPixivUser()

def main():
    init()
    doChoice()   

if __name__ == '__main__':
    main()
