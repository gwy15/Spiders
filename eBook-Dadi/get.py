import time
import re
import requests
from bs4 import BeautifulSoup as bs

import ProgressBar

url = 'http://www.my285.com/wgwx/cpxs/dadi/%03d.htm'

class My285Book:
    def __init__(self, url, start, end):
        self.url = url
        self.headers = {
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
            'Cookie':'Hm_lvt_9e49ea2ec9c7da90d2fc4246e717f460=1492345083; Hm_lpvt_9e49ea2ec9c7da90d2fc4246e717f460=1492345095'
        }
        self.bar = ProgressBar.ProgressBar(end-start+1)
        self.bar.grow(0)
        self.get(start, end)
    
    def get(self, start, end):
        with open('out.txt', 'w', encoding='utf8') as f:
            for page in range(start, end+1):
                text = self.getPage(page)
                time.sleep(2)
                print(text, file = f)
                # print(f'{page} finished.')
                self.bar.grow()
    
    def getPage(self, page):
        try:
            return self._getPage(page)
        except:
            time.sleep(2)
            return self._getPage(page)

    def _getPage(self, page):
        url = self.url%page
        content = requests.get(url, headers=self.headers).content
        # print(content)
        content = content.decode('gbk')
        # print(content)
        soup = bs(content, 'html.parser')
        soup = soup.find_all('td', {'colspan':"2"})
        soup = soup[2]

        text = soup.text
        text = re.sub(r'^[\r\n]+', '', text)
        text = re.sub(r'\s+$', '\n\n', text)
        return text

def main():
    My285Book(url, int(input('start')), int(input('end')))

if __name__ == '__main__':main()
