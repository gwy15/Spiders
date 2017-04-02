import re, json, os
import requests
from bs4 import BeautifulSoup as bs
import Niconvert

class VideoItem():
    def __init__(self, id):
        self.aid = id

    def run(self, aid=None, title=None):
        """
        通过 av 号，下载并转换所有的弹幕。
        """
        if aid is None:
            aid = self.aid
        CidInfo = self.getCidInfoFromAid(aid)

        for item in CidInfo:
            if title is None:
                if len(CidInfo) == 1:
                    ptitle = self.getSingleTitle(aid)
                else:
                    ptitle = item[1]
            else:
                ptitle = title
            self.getDanmu(item[0], ptitle)
            print('cid = %d, title = %s'%(item[0], ptitle))
            
    def getDanmu(self, cid, title):
        xmlDanmu = self.getXMLDanmu(cid)
        self.writeXML(xmlDanmu, title)
        assDanmu = Niconvert.convert(xmlDanmu)
        self.writeAss(assDanmu, title)

    def getSingleTitle(self, aid):
        url = 'https://www.bilibili.com/video/av%d/'%aid
        page = requests.get(url).content.decode()
        
        soup = bs(page, 'html.parser')
        title = soup.head.title.text
        title.replace(' 番剧 bilibili 哔哩哔哩弹幕视频网', '')
        title = re.sub(r'_.{2,}_.{2,}_bilibili_哔哩哔哩', '', title)
        title.replace('?', '？')
        title = re.sub(r'[\\/:*?"<>|]', '', title)
        return title

    def getCidInfoFromAid(self, aid):
        r'''
        通过 av 号得到所有的 cid，返回 [(cid, title, page)]
        '''
        url = 'http://www.bilibili.com/widget/getPageList?aid=%d'%aid
        page = requests.get(url).content.decode()
        js = json.loads(page)
        res = []
        for item in js:
            res.append((int(item['cid']), item['pagename'], int(item['page'])))
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

class Bangumi(VideoItem):
    def __init__(self, id):
        self.banguimiID = id
    def banguimiRun(self):
        episodeInfo = self.getEpisodeInfoFromBangumiID(self.banguimiID)
        s = set()
        for item in episodeInfo:
            s.add(item[0])
        if len(s) == 1: # 同 av
            self.run(episodeInfo[0][0])
        else:
            for item in episodeInfo:
                self.run(item[0], title=(item[1] + ' ' + item[3]))

    def getEpisodeInfoFromBangumiID(self, BID):
        r'''
        返回 banguimi ID 的信息 
        rtype: [(av, index, episode_id, index_title)]
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

        res = []
        for item in js['result']['episodes']:
            res.append((int(item['av_id']), item['index'], int(item['mid']), item['index_title']))
        return res

class DanmuGetter():
    def __init__(self, identifier):
        r'''
        通过 identifier，找到对应的 av 号。
        '''
        self.isBangumi = False
        if isinstance(identifier, str):
            if re.match(r'(https?://)?bangumi\.bilibili\.com/anime/(\d+)/?', identifier):
                bangumiID = int(re.findall(r'\d+', identifier)[0])
                Bangumi(bangumiID).banguimiRun()
            elif re.match(r'(https?://)?www\.bilibili\.com/video/av\d+/?', identifier):
                aid = int(re.findall(r'\d+', identifier)[0])
                VideoItem(aid).run()
            else:
                print('str no match. str = %s'%identifier)
                quit()
        elif isinstance(identifier, int):
            VideoItem(identifier).run()

if __name__=='__main__':
    DanmuGetter(1687843) # 单 P 测试
    DanmuGetter('https://www.bilibili.com/video/av5415480') # 多 P 测试
    DanmuGetter('http://bangumi.bilibili.com/anime/2993')   # 番组测试（同 av)
    DanmuGetter('https://bangumi.bilibili.com/anime/5800/') # 番组测试（不同 av)
