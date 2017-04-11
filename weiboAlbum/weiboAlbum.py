import re
import json
import os, os.path
import traceback
import time
import random
from multiprocessing.dummy import Pool as ThreadPool

import requests

class WeiboAlbum():
    def __init__(self, page_id, root='images'):
        self.page_id = page_id
        self.root = root
        self.url = 'http://weibo.com/p/%d/photos'%page_id
    
    def run(self):
        if not os.path.exists(self.root):
            os.mkdir(self.root)
        self.getConfig()

    def downloadPage(self, n):
        url = f'http://weibo.com/p/aj/album/loading?ajwvr=6&type=photo&page_id={self.page_id}&page={n}&ajax_call=1'
        try:
            # FIXME
            photosList = self.getPhotoslist('http://weibo.com/p/%d/photos'%self.page_id)
            addresses = self.getPhotosAddresses(photosList)
            self.downloadPhotos(addresses)
        except:
            print('except at run')
            traceback.print_exc()

    def getConfig(self):
        '读取配置文件'
        with open('config.json', 'r') as f:
            js = json.loads(f.read())
            self.headers = js['headers']

    def getPhotoslist(self, url):
        '读取相册里的图片列表。返回 [(uid, mid, pid)]'
        content = self.getContent(self.url)
        if not content: return None
        li = re.findall(r'uid=(\d+)&mid=(\d+)&pid=([\d\w]+)&', content)
        return li

    def getContent(self, url):
        '返回 url 的 content'
        response = self.getResponse(url)
        if response is None: return None
        content = response.content.decode('utf-8')
        return content

    def getResponse(self, url):
        '返回 url 的 response'
        try:
            res = requests.get(url, headers=self.headers)
            return res
        except:
            print(f'get url {url} failed.')
            return None

    def getPhotosAddresses(self, photosList):
        '解析图片的直链地址，返回 [url]'
        photosAddresses = set()

        def task(tup):
            photoAddress = self.getPhotoAddress(tup)
            photosAddresses.add(photoAddress)
            print(f'get adress: {photoAddress}')
            time.sleep(0.5 + random.random())

        pool = ThreadPool(10)
        pool.map(task, photosList)
        pool.close()
        return photosAddresses

    def getPhotoAddress(self, tup:tuple):
        '解析对应 uid, mid, pid 的图片直链'
        uid, mid, pid = tup
        url = f'http://photo.weibo.com/{uid}/wbphotos/large/mid/{mid}/pid/{pid}'
        content = self.getContent(url)
        if not content: return
        res = re.findall(r'http://.*\.sinaimg.cn/large/[\d\w]+.jpg', content)
        if len(res) != 1:
            print('find multi targets in getPhotoAddress')
            print(res)
        return res[0]

    def downloadPhotos(self, photosAddresses):
        '下载图片直链列表里面的图片'
        def task(url):
            self.downloadPhoto(url)
            print(f'complete: {url}')
            time.sleep(0.5 + random.random())
        pool = ThreadPool(10)
        pool.map(task, photosAddresses)
        pool.close()
    
    def downloadPhoto(self, photoAdress):
        '下载直链对应的图片'
        response = self.getResponse(photoAdress)
        if response is None: return None
        fileName = self.getName(photoAdress)
        with open(fileName, 'wb') as f:
            f.write(response.content)
    
    def getName(self, url):
        '从直链里面解析图片命名'
        fileName = re.findall(r'/([^/]+\.(jpg|png|bmp|jpeg|webm|JPG|PNG|BMP|JPEG|WEBM))', url)[0][0]
        fileName = os.path.join(self.root, fileName)
        return fileName

def main():
    WeiboAlbum(1005055913848279).run()

if __name__ == '__main__':
    main()