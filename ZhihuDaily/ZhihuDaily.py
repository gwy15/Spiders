import requests
from bs4 import BeautifulSoup as bs

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
        finally:
            pass
        
    def parse(self, content:str):
        if not content:
            self.title = None
            return None
        soup = bs(content, 'html.parser')
        self.title = soup.title.text
    
    def print(self):
        print('%8d  %s'%(self.id, self.title))

def main():
    ZhihuDaily(1).print()

if __name__ == '__main__':
    main()
    