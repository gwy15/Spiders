from multiprocessing.dummy import Pool as ThreadPool

import requests
from bs4 import BeautifulSoup as bs

# import ProgressBar

class ZhihuDaily():
    def __init__(self, id):
        self.id = id
        url = 'http://daily.zhihu.com/story/%d'%id
        content = self.getResponseContent(url)
        self.parse(content)
    
    def getResponseContent(self, url):
        try:
            res = requests.get(
                url,
                headers = {
                    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'
                }
            )
            if res.status_code != 200:
                # print(res.status_code)
                return None
            content = res.content.decode()
            return content
        except requests.exceptions.BaseHTTPError:
            print('except at id = %d'%self.id)
            return None
        finally:
            pass
        
    def parse(self, content:str):
        if content is None:
            self.title = None
            return None
        soup = bs(content, 'html.parser')
        self.title = soup.title.text
    
    def print(self):
        if self.title:
            print('%8d  %s'%(self.id, self.title))

def main():
    pool = ThreadPool(10)
    def task(i):
        ZhihuDaily(i).print()
    pool.map(task, range(100))
    pool.close()
        

if __name__ == '__main__':
    main()
    