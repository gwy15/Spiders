import re, json, os
import requests
from bs4 import BeautifulSoup as bs
import Niconvert

class Danmu():
    def __init__(self, identifier):
        r'''
        通过 identifier，找到对应的 av 号。
        '''
        self.isBangumi = False
        if isinstance(identifier, str):
            if re.match(r'(https?://)?bangumi\.bilibili\.com/anime/(\d+)/', identifier):
                self.isBangumi = True
                self.bangumiID = int(re.findall(r'\d+', identifier)[0])
                self.aid = self.getAidFromBangumiID(self.bangumiID)
            elif re.match(r'(https?://)?www\.bilibili\.com/video/av\d+/', identifier):
                self.aid = int(re.findall(r'\d+', identifier)[0])
            else:
                print('str no match. str = %s'%identifier)
                quit()
        elif isinstance(identifier, int):
            self.aid = identifier

    def run(self):
        r"""
        通过 av 号，下载并转换所有的弹幕。
        """
        self.titleCidDict = self.getCidDictFromAid(self.aid)
        print(self.titleCidDict)
        for cid in self.titleCidDict.keys():
            xmlDanmu = self.getXMLDanmu(cid)
            self.writeXML(xmlDanmu, self.titleCidDict[cid])
            assDanmu = Niconvert.convert(xmlDanmu)
            self.writeAss(assDanmu, self.titleCidDict[cid])

    def getAidFromBangumiID(self, BID):
        r'''
        返回 banguimi ID 对应的 Av 号
        '''
        url = 'http://bangumi.bilibili.com/jsonp/seasoninfo/%d.ver?&jsonp=jsonp'%BID
        page = requests.get(url).content.decode()
        try:
            js = json.loads(page)
        except:
            try:
                js = json.loads(page[19:-2])
            except:
                print('failed in getAidFromBangumiID(bid = %d)'%BID)
                return

        self.urls = []
        for item in js['result']['episodes']:
            self.urls.append(item['webplay_url'])

        return js['result']['episodes'][0]['av_id']


            

    def getTitle(self, ):
        page = requests.get(url).content.decode()
        
        soup = bs(page, 'html.parser')
        self.title = soup.head.title.text
        self.title.replace(' 番剧 bilibili 哔哩哔哩弹幕视频网', '')
        self.title = re.sub(r'_.{2}_.{2}_bilibili_哔哩哔哩', '', self.title)
        self.title.replace('?', '？')
        self.title = re.sub(r'[\\/:*?"<>|]', '', self.title)
        print(self.title)



    def getCidDictFromAid(self, aid):
        r'''
        通过 av 号得到所有的 cid，储存在一个 Dict 中，dict[cid] = title。
        '''
        url = 'http://www.bilibili.com/widget/getPageList?aid=%d'%aid
        page = requests.get(url).content.decode()
        js = json.loads(page)
        res = {}
        for item in js:
            res[int(item['cid'])] = item['pagename']
        return res

    def getXMLDanmu(self, cid):
        r'''
        获取 XML 格式弹幕
        '''
        xmlurl = 'http://comment.bilibili.com/%d.xml'%int(cid)
        xml = requests.get(xmlurl).content.decode()
        return xml

    def writeAss(self, ass, filename):
        if not os.path.exists('ass'):
            os.mkdir('ass')
        with open(os.path.join('ass', '%s.ass'%(filename)), 'w', encoding='utf-8') as f:
            f.write(ass)
    def writeXML(self, xml, filename):
        if not os.path.exists('xml'):
            os.mkdir('xml')
        with open(os.path.join('xml', '%s.xml'%(filename)), 'w', encoding='utf-8') as f:
            f.write(xml)

if __name__=='__main__':
    Danmu(5415480).run()
    # Danmu('http://bangumi.bilibili.com/anime/2993/').run()