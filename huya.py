# 获取虎牙直播的真实流媒体地址。
# 虎牙"一起看"频道的直播间可能会卡顿，尝试将返回地址 tx.hls.huya.com 中的 tx 改为 bd、migu-bd。

import requests
import re
import base64
import urllib.parse
import hashlib
import time
from bs4 import BeautifulSoup


class HuYa:

    def __init__(self, rid):
        self.rid = rid

    def get_real_url(self):
        try:
            room_url = 'https://m.huya.com/' + str(self.rid)
            header = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'User-Agent': 'Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 '
                              '(KHTML, like Gecko) Chrome/75.0.3770.100 Mobile Safari/537.36 '
            }
            response = requests.get(url=room_url, headers=header).text
            livelineurl = re.findall(r'liveLineUrl = "([\s\S]*?)";', response)[0]
            livelineurl = base64.b64decode(livelineurl).decode('utf-8')
            if livelineurl:
                if 'replay' in livelineurl:
                    real_url = {
                        'replay': "https:" + livelineurl,
                    }
                else:
                    s_url = self.live(livelineurl)
                    b_url = self.live(livelineurl.replace('_2000', ''))
                    real_url = {
                        '2000p': "https:" + s_url,
                        'tx': "https:" + b_url,
                        'bd': "https:" + b_url.replace('tx.hls.huya.com', 'bd.hls.huya.com'),
                        'migu-bd': "https:" + b_url.replace('tx.hls.huya.com', 'migu-bd.hls.huya.com'),
                    }
            else:
                raise Exception('未开播或直播间不存在')
        except Exception as e:
            raise Exception('未开播或直播间不存在')
        return real_url

    @staticmethod
    def live(e):
        i, b = e.split('?')
        r = i.split('/')
        s = re.sub(r'.(flv|m3u8)', '', r[-1])
        c = b.split('&', 3)
        c = [i for i in c if i != '']
        n = {i.split('=')[0]: i.split('=')[1] for i in c}
        fm = urllib.parse.unquote(n['fm'])
        u = base64.b64decode(fm).decode('utf-8')
        p = u.split('_')[0]
        f = str(int(time.time() * 1e7))
        ll = n['wsTime']
        t = '0'
        h = '_'.join([p, t, s, f, ll])
        m = hashlib.md5(h.encode('utf-8')).hexdigest()
        y = c[-1]
        url = "{}?wsSecret={}&wsTime={}&u={}&seqid={}&{}".format(i, m, ll, t, f, y)
        return url

    def get_yqk_content(self):
        content='虎牙,#genre#\n'
        url ='https://www.huya.com/g/seeTogether'
        text = requests.get(url).text
        soup = BeautifulSoup(text, 'html.parser')
        for ultag  in soup.find_all('ul', {'class': 'live-list clearfix'}):
             for litag in ultag.find_all('li'):
                if litag:
                    content += ('{},http://192.168.123.2:8088/huya{}\n'.format(litag.find('a',{'class','title'}).text,litag.find('a',{'class','title'}, href=True)['href'].replace('https://www.huya.com','')))
        return content

def get_real_url(rid):
    try:
        hy = HuYa(rid)
        return hy.get_real_url()
    except Exception as e:
        print('Exception：', e)
        return False
        


if __name__ == '__main__':
    rid = input('输入虎牙直播房间号：\n')
    print(get_real_url(rid))

