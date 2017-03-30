import requests
import json

def getLyric(songId):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.138 Safari/537.36",
        'Cookie': 'appver=1.5.0.75771;',
        'Referer': 'http://music.163.com/'
    }
    url = 'http://music.163.com/api/song/lyric?os=pc&id=%d&lv=-1&kv=-1&tv=-1'%(songId)
    r = requests.get(url, headers=headers)
    c = r.content.decode()
    js = json.loads(c)
    return js['lrc']['lyric'] + '\n' + js['tlyric']['lyric']

if __name__=='__main__':
    s = getLyric(22705495)
    with open('lrc.txt', 'w', encoding='utf8') as f:
        print(s, file=f)