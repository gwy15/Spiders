import sys
import re
import os, getpass, json
import traceback
import time, random
from multiprocessing.dummy import Pool as ThreadPool
from multiprocessing.dummy import Lock as ThreadLock

import requests
from bs4 import BeautifulSoup as bs
import pymysql

import ProgressBar

class steamItem():
    def __init__(self, appId):
        self.id = appId
        self.url = 'https://store.steampowered.com/widget/%d/'%appId
        self.exists = True
        self.title = None
        self.desc = None
        self.discount = None
        self.discountPercent = None
        self.price = None
        self.originalPrice = None
        self.finalPrice = None

    def _getSoup(self):
        headers = {
            'Accept-Language':'zh-CN,zh;q=0.8',
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
        }
        response = requests.get(self.url, headers=headers)
        content = response.content.decode()
        soup = bs(content, 'html.parser')
        return soup

    def get(self):
        soup = self._getSoup()

        self.title = self._getTitle(soup)
        if not self.exists:
            return None

        self.desc = self._getDesc(soup)
        
        self._getPrice(soup)

    def _getDesc(self, soup:bs):
        desc = soup.body.div.find('div', {'class':'desc'}).text
        return re.sub(r"^\s+", '', desc)

    def _getTitle(self, soup:bs):
        title = soup.head.title.text
        if title == '错误':
            self.exists = False
            return None
        return self._extractTitle(title)

    def _getPrice(self, soup:bs, isPack = False):
        if not isPack:
            s1 = soup.find('div', {'class':'game_purchase_action_bg'})
        else:
            s1 = soup.find_all('div', {'class':'game_purchase_action_bg'})[1]
        if self.discount:
            self.discountPercent = s1.find('div', {'class':'discount_pct'}).text[1:-1]
            self.originalPrice   = s1.find('div', {'class':'discount_original_price'}).text[2:]
            self.finalPrice      = s1.find('div', {'class':'discount_final_price'}).text[2:]
        else:
            try:
                self.price = re.sub(r'^\s+', '', s1.find('div', {'class':'game_purchase_price price'}).text)[2:]
            except:
                buttonText = s1.find('a', {'class':'btn_addtocart_content'}).text
                if '开始游戏' in buttonText or '安装游戏' in buttonText:
                    self.price = 0
                elif '礼包信息' in buttonText:
                    self.isPack = True
                    return self._getPrice(soup, True)
                else:
                    self.price = None

    def _extractTitle(self, strWebTitle):
        if strWebTitle[:5] == 'Steam':
            self.discount = False
            return strWebTitle[9:]
        else:
            self.discount = True
            strWebTitle = strWebTitle[12:]
            strWebTitle = re.sub(r' 立省 \d{1,3}%', '', strWebTitle)
            return strWebTitle
    
    def _print(self):
        print(self.id)
        print(self.title)
        print(self.desc)
        if self.discount:
            print('\tdiscount.    %s -> %s, %s%% off'%(self.originalPrice, self.finalPrice, self.discountPercent))
        else:
            print('\tno discount. %s'%self.price)
        print('--'*30)
    def _escapeChar(self):
        def es(s):
            if s is None:
                return s
            if isinstance(s, str):
                s = s.replace("'", "''")
                s = s.replace('\\', '\\\\')
                return s
        self.title = es(self.title)
        self.desc = es(self.desc)
    def _insert(self, cur:pymysql.cursors.Cursor):
        self._escapeChar()
        cur.execute(r"""
            SELECT `InDiscount` from `Apps`
            WHERE `AppID` = '%s'
            LIMIT 1;"""%self.id)
        f = cur.fetchall()
        if len(f) == 0: # not exists, insert
            self._insertIntoAppsTable(cur)
            if self.discount:
                self._insertIntoDiscountAppsTable(cur)
        else: # exists
            self._updateAppsTable(cur)
            if not f[0][0]: # not in discount before
                if self.discount:
                    self._insertIntoDiscountAppsTable(cur)
            else: # discount before
                if self.discount:
                    self._updateDiscountAppsTable(cur)
                else:
                    self._removeDiscountAppsTable(cur)


    def _insertIntoAppsTable(self, cur):
        if not self.discount:
            cur.execute(r"""
                INSERT INTO `Apps`
                (`AppID`, `Name`, `Description`, `Price`, `InDiscount`)
                VALUES
                ('%s',    '%s',   '%s',          '%s',    '%s');
            """%(self.id, self.title, self.desc, self.price, '0'))
        else:
            cur.execute(r"""
                INSERT INTO `Apps`
                (`AppID`, `Name`, `Description`, `Price`, `InDiscount`)
                VALUES
                ('%s',    '%s',   '%s',          '%s',    '%s');
            """%(self.id, self.title, self.desc, self.finalPrice, '1'))
    def _insertIntoDiscountAppsTable(self, cur):
        cur.execute(r"""
            INSERT INTO `DiscountApps`
            (`AppID`, `DiscountPercent`, `OriginalPrice`, `FinalPrice`)
            VALUES
            ('%s',    '%s',              '%s',            '%s');
        """%(self.id, self.discountPercent, self.originalPrice, self.finalPrice))
    def _updateAppsTable(self,cur):
        if not self.discount:
            cur.execute(r"""
                UPDATE `Apps` SET
                `Name` = '%s', `Description` = '%s', `Price` = '%s', `InDiscount` = '0'
                WHERE `AppID` = '%s';
            """%(self.title, self.desc, self.price, self.id))
        else: # now in discount
            cur.execute(r"""
                UPDATE `Apps` SET
                `Name` = '%s', `Description` = '%s', `Price` = '%s', `InDiscount` = '1'
                WHERE `AppID` = '%s';
            """%(self.title, self.desc, self.finalPrice, self.id))
    def _updateDiscountAppsTable(self, cur):
        cur.execute(r"""
            UPDATE `DiscountApps` SET
            `DiscountPercent` = '%s', `OriginalPrice` = '%s', `FinalPrice` = '%s'
            WHERE `AppID` = '%s';
            """%(self.discountPercent, self.originalPrice, self.finalPrice, self.id))
    def _removeDiscountAppsTable(self, cur):
        cur.execute(r"""
            DELETE FROM `DiscountApps`
            WHERE `AppID` = '%s';
        """%self.id)

def getSteamItem(id, conn:pymysql.connections.Connection, lock):
    try:
        s = steamItem(id)
        s.get()
        if not s.exists:
            return
    
        cur = conn.cursor()
        lock.acquire()
        try:
            cur.execute('USE `steam`;')
            s._insert(cur)
            conn.commit()
        except:
            pass
        finally:
            lock.release()
        time.sleep(random.random())
        return
    except Exception as ex:
        print('---'*20)
        print('%s failed.'%s.id)
        print(ex)
        traceback.print_exc()
        try:
            s._print()
        except:
            pass
        print('---'*20)
        return

def login():
    try:
        with open('login.conf', 'r') as f:
            j = json.loads(f.read())
            user = j['user']
            pswd = j['pswd']
    except:
        user = input('input username: ')
        pswd = getpass.getpass("input password: ")

    return pymysql.connect(
            host='localhost',
            user=user, passwd=pswd,
            port=3306, charset='utf8')

def main(n = 1, m = 1000):
    if len(sys.argv) >= 3:
        n = int(sys.argv[1])
        m = int(sys.argv[2])
    
    conn = login()
    
    bar = ProgressBar.ProgressBar(m-n+1, 40, printTime=True)
    pool = ThreadPool(16)
    lock = ThreadLock()
    def target(i):
        res = getSteamItem(i, conn, lock)
        bar.grow()
    pool.map(target, range(n, m+1))
    pool.close()
    pool.join()

if __name__ == '__main__':
    main()
