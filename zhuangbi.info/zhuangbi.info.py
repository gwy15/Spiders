import sys, time, os, os.path, re
from multiprocessing.dummy import Pool as ThreadPool

import requests
from bs4 import BeautifulSoup as bs

import ProgressBar

class ZhuangbiGetter():
    def __init__(self, pages=1):
        self.n = pages
        self.headers={
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36"
        }
        self.bar = ProgressBar.ProgressBar(20*pages, 40)
        if not os.path.exists('img'):
            os.mkdir('img')
        print('init complete')    
        
    def get(self) -> None:
        pool = ThreadPool(min(4, self.n))
        pool.map(self.getSingePage, [i+1 for i in range(self.n)])
        pool.close()
        pool.join()

    def getSingePage(self, i:int) -> None:
        '''
        download imgs of a whole page.
        '''
        li = self.getPicList(i)
        pool = ThreadPool(10)
        pool.map(self.getPic, li)
        pool.close()
        pool.join()

    def getPic(self, tup:tuple) -> None:   
        try:
            name, url = tup
            return self._getPic(name, url)
        except:
            print('exception')
        finally:
            self.bar.grow()

    def _getPic(self, name:str, url:str) -> None:
        '''
        download the url and save as the name.
        return directly if pic already exists.
        '''
        name = self.formatName(name)
        filename = name + '.' + os.path.splitext(url[-10:])[1][1:] # add ext name
        filename = os.path.join('img', filename)                   # add dir name
        if os.path.exists(filename):
            return
        else:
            img = requests.get(url, headers=self.headers).content
            with open(filename, 'wb') as f:
                f.write(img)
            return

    def getPicList(self, i:int) -> [(str, str)]:
        '''
        get names and urls for page number `i`
        rtype: [(strName, strURL), ]
        '''
        url = 'https://www.zhuangbi.info/?page=%d'%i
        r = requests.get(url, headers=self.headers)
        c = r.content.decode('utf-8')
        soup = bs(c, 'html.parser')
        imglist = soup.find_all('div', {'class':'picture-list'})[1]
        imgs = imglist.find_all('img', {'class':'thumbnail'})
        res = []
        for item in imgs:
            title = item['alt']
            imgurl = item['src']
            _ = re.findall(
                r'http[^\?]+',
                imgurl)
            if len(_) == 0:
                print(imgurl)
            else:
                imgurl = _[0]
            res.append((title, imgurl))
        return res

    def formatName(self, name:str):
        name = name.replace(':', '：').replace('*', '※').replace('?', '？')
        name = re.sub(r'\\/<>\|', '', name)
        return name

def main(n=10):
    getter = ZhuangbiGetter(n)
    getter.get()

if __name__=='__main__':
    n = 10
    if len(sys.argv) > 1:
        if sys.argv[1].isdigit():
            n = int(sys.argv[1])
    main(n)
