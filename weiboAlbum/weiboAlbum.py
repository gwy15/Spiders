import re
import json
import os, os.path
import traceback
import time
from multiprocessing.dummy import Pool as ThreadPool

import requests

class WeiboAlbum():
    def __init__(self, id, root='images'):
        self.id = id
        self.root = root
        self.url = 'http://weibo.com/p/%d/photos'%id
    
    def run(self):
        try:
            if not os.path.exists(self.root):
                os.mkdir(self.root)
            self.getConfig()
            photosList = self.getPhotoslist()
            addresses = self.getPhotosAddresses(photosList)
            self.downloadPhotos(addresses)
        except:
            print('except at run')
            traceback.print_exc()

    def getConfig(self):
        with open('config.json', 'r') as f:
            js = json.loads(f.read())
            self.headers = js['headers']

    def getPhotoslist(self):
        content = self.getContent(self.url)
        if not content: return None
        li = re.findall(r'uid=(\d+)&mid=(\d+)&pid=([\d\w]+)&', content)
        return li

    def getContent(self, url):
        response = self.getResponse(url)
        if response is None: return None
        content = response.content.decode('utf-8')
        return content
        

    def getResponse(self, url):
        try:
            res = requests.get(url, headers=self.headers)
            return res
        except:
            print(f'get url {url} failed.')
            return None

    def getPhotosAddresses(self, photosList):
        photosAddresses = set()

        def task(tup):
            uid, mid, pid = tup
            url = f'http://photo.weibo.com/{uid}/wbphotos/large/mid/{mid}/pid/{pid}'
            content = self.getContent(url)
            if not content: return
            photoAddress = self.getPhotoAddress(content)
            photosAddresses.add(photoAddress)
            print(f'get adress: {photoAddress}')
            time.sleep(0.5)

        pool = ThreadPool(10)
        pool.map(task, photosList)
        pool.close()
        return photosAddresses

    def getPhotoAddress(self, content:str):
        res = re.findall(r'http://.*\.sinaimg.cn/large/[\d\w]+.jpg', content)
        if len(res) != 1:
            print('find multi targets in getPhotoAddress')
            print(res)
        return res[0]

    def downloadPhotos(self, photosAddresses):
        def task(url):
            self.downloadPhoto(url)
            print(f'complete: {url}')
        pool = ThreadPool(10)
        pool.map(task, photosAddresses)
        pool.close()
    
    def downloadPhoto(self, photoAdress):
        response = self.getResponse(photoAdress)
        if response is None: return None
        fileName = self.getName(photoAdress)
        with open(fileName, 'wb') as f:
            f.write(response.content)
    
    def getName(self, url):
        fileName = re.findall(r'/([^/]+\.(jpg|png|bmp|jpeg|webm|JPG|PNG|BMP|JPEG|WEBM))', url)[0][0]
        fileName = os.path.join(self.root, fileName)
        return fileName

def main():
    WeiboAlbum(1005056159370668).run()

if __name__ == '__main__':
    main()