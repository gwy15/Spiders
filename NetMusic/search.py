import requests, json

def search(string):
    try:
        res = _search(string)
    except Exception as ex:
        print(ex)
        res = [dict()]
    finally:
        return res

def _search(string):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.138 Safari/537.36",
        'Cookie': 'appver=1.5.0.75771;',
        'Referer': 'http://music.163.com/'
    }

    data = {'s':string, 'offset':'0', 'limit':'10','type':'1'}
    target = 'http://music.163.com/api/search/pc'
    
    r = requests.post(target, headers=headers, data=data)
    res = json.loads(r.content.decode())

    assert(res['code']==200)
    res = res['result']['songs']

    return res

if __name__=='__main__':
    s = search('彩虹')
    with open('out.txt', 'w', encoding='utf8') as f:
        for item in s:
            for key in item:
                f.write('%s: %s\n'%(key, item[key]))
            f.write('\n')