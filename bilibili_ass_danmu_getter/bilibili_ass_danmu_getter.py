import re, json, os
import requests
from bs4 import BeautifulSoup as bs
import Niconvert

class BaseVideo():
    def __init__(self, assRoot='ass', xmlRoot='xml'):
        self.assRoot = assRoot
        self.xmlRoot = xmlRoot
    def getDanmu(self, cid, title):
        '''
        通过 cid 下载弹幕
        '''
        xmlDanmu = self.getXMLDanmu(cid)
        self.writeXML(xmlDanmu, title)
        assDanmu = Niconvert.convert(xmlDanmu)
        self.writeAss(assDanmu, title)
        print('%d\t%s finished.'%(cid, title))

    def getXMLDanmu(self, cid):
        r'''
        获取 XML 格式弹幕
        '''
        xmlurl = 'http://comment.bilibili.com/%d.xml'%int(cid)
        xml = requests.get(xmlurl).content.decode()
        return xml

    def writeAss(self, ass, filename):
        if not os.path.exists(self.assRoot):
            os.mkdir(self.assRoot)
        with open(os.path.join(self.assRoot, '%s.ass'%(filename)), 'w', encoding='utf-8') as f:
            f.write(ass)
    def writeXML(self, xml, filename):
        if not os.path.exists(self.xmlRoot):
            os.mkdir(self.xmlRoot)
        with open(os.path.join(self.xmlRoot, '%s.xml'%(filename)), 'w', encoding='utf-8') as f:
            f.write(xml)

class VideoItem(BaseVideo):
    def __init__(self, aid, assRoot = 'ass', xmlRoot = 'xml'):
        self.aid = aid
        self.assRoot = assRoot
        self.xmlRoot = xmlRoot

    def run(self):
        """
        通过 av 号，下载并转换所有的弹幕。
        """
        CidInfo = self.getCidInfoFromAid(self.aid)
        for item in CidInfo:
            cid = item[0]
            if len(CidInfo) == 1: # 单 P
                title = self.getSingleTitle(self.aid)
            else:
                title = item[1]
            self.getDanmu(cid, title) # 使用分 P 的标题

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
        通过 av 号得到所有的分 P 信息，返回 [(cid, title, page)]
        '''
        url = 'http://www.bilibili.com/widget/getPageList?aid=%d'%aid
        page = requests.get(url).content.decode()
        js = json.loads(page)
        res = []
        for item in js:
            res.append((int(item['cid']), item['pagename'], int(item['page'])))
        return res

class BanguimiEpisode(BaseVideo):
    def __init__(self, episodeID, assRoot = 'ass', xmlRoot = 'xml'):
        self.episodeID = episodeID
        self.assRoot = assRoot
        self.xmlRoot = xmlRoot

    def run(self):
        self.getEpisodeDanmu(self.episodeID)

    def getEpisodeDanmu(self, episodeID):
        index, title, cid = self.getSingleEpisodeInfo(episodeID)
        self.getDanmu(cid, index+' '+title)

    def getSingleEpisodeInfo(self, episodeID):
        '''
        返回 [(indexTitle, title, cid), ]
        '''
        url = 'http://bangumi.bilibili.com/web_api/episode/%d.json'%episodeID
        c = requests.get(url).content.decode()
        js = json.loads(c)
        j = js['result']['currentEpisode']
        return (j['indexTitle'], j['longTitle'], int(j['danmaku']))

class Bangumi():
    def __init__(self, bid, assRoot='ass', xmlRoot='xml'):
        self.banguimiID = bid
        self.assRoot = assRoot
        self.xmlRoot = xmlRoot

    def run(self):
        episodesInfo = self.getEpisodesInfoFromBangumiID(self.banguimiID)
        for item in episodesInfo:
            eID = item[2]
            BanguimiEpisode(eID, self.assRoot, self.xmlRoot).run()

    def getEpisodesInfoFromBangumiID(self, BID):
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
        try:
            self.title = js['result']['bangumi_title']
        except:
            self.title = '获取番组名字出错'

        res = []
        for item in js['result']['episodes']:
            res.append((int(item['av_id']), item['index'], int(item['episode_id']), item['index_title']))
        return res

class DanmuGetter():
    def __init__(self, identifier, isbangumi=False):
        '''
        通过 identifier，找到对应的 av 号。
        '''
        if isinstance(identifier, str):
            # 单集匹配
            if re.match(r'(https?://)?bangumi\.bilibili\.com/anime/\d+/play#\d+?', identifier):
                episodeID = int(re.findall(r'play#(\d+)', identifier)[0])
                BanguimiEpisode(episodeID).run()
            # 整个番组
            elif re.match(r'(https?://)?bangumi\.bilibili\.com/anime/(\d+)/?', identifier):
                bangumiID = int(re.findall(r'\d+', identifier)[0])
                Bangumi(bangumiID).run()
            # 一般视频
            elif re.match(r'(https?://)?www\.bilibili\.com/video/av\d+/?', identifier):
                aid = int(re.findall(r'\d+', identifier)[0])
                VideoItem(aid).run()
            else:
                print('str no match. str = %s'%identifier)
                quit()
        elif isinstance(identifier, int):
            if isbangumi:
                Bangumi(identifier).run()
            else:
                VideoItem(identifier).run()

def main():
    import sys
    if len(sys.argv) > 1:
        isbangumi = True
        id = None
        for item in sys.argv[1:]:
            if item[0] == '-':
                isbangumi = True if item[1] == 'b' else False
            if item.isdecimal():
                id = int(item)
        DanmuGetter(id, isbangumi)
    else:
        DanmuGetter(input('input: '))
        


def test():
    DanmuGetter(1687843) # 单 P 测试
    DanmuGetter('https://www.bilibili.com/video/av5415480') # 多 P 测试
    DanmuGetter('http://bangumi.bilibili.com/anime/2993')   # 番组测试（同 av)
    DanmuGetter('https://bangumi.bilibili.com/anime/5800/') # 番组测试（不同 av)
    DanmuGetter('https://bangumi.bilibili.com/anime/5563/play#96502') # 单集测试
    

if __name__=='__main__':
    main()
    # test()
