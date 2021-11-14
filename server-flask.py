from flask import Flask,request, jsonify,redirect,make_response
from douyu import DouYu
from youku import YouKu
from bs4 import BeautifulSoup
from expiringdict import ExpiringDict
import requests
app = Flask(__name__)

cache = ExpiringDict(max_len=100, max_age_seconds=300)
@app.route('/<plat>/<rid>')
def get_url(plat,rid):
    if 'huya' == plat:
        # h = HuYa(rid)
        url = get_real_url(rid)
    elif 'douyu'  == plat:
        d = DouYu(rid)
        url = d.get_real_url()
    elif 'youku' == plat:
        y = YouKu(rid)
        url = y.get_real_url()
    print(url)
    return redirect(url, code=302)

def get_nick(item):
    if item:
        return item.text + '-'
    return ''
def get_douyu_content(group,name):
    content=name+',#genre#\n'
    url ='https://www.douyu.com/' + group
    text = requests.get(url).text
    soup = BeautifulSoup(text, 'html.parser')
    for ultag  in soup.find_all('ul', {'class': 'layout-Cover-list'}):
         for litag in ultag.find_all('li'):
            if litag:
                content += ('{},http://192.168.123.2:8088/douyu{}\n'.format(get_nick(litag.find('div',{'class','DyListCover-userName'}))  + litag.find('h3',{'class','DyListCover-intro'}).text,litag.find('a', href=True)['href']))
    return content

def get_huya_content(group,name):
    content=name+',#genre#\n'
    url ='https://www.huya.com/g/' + group
    text = requests.get(url).text
    soup = BeautifulSoup(text, 'html.parser')
    for ultag  in soup.find_all('ul', {'class': 'live-list clearfix'}):
         for litag in ultag.find_all('li'):
            if litag:
                content += ('{},http://192.168.123.2:8088/huya{}\n'.format(get_nick(litag.find('i',{'class','nick'})) + litag.find('a',{'class','title'}).text,litag.find('a',{'class','title'}, href=True)['href'].replace('https://www.huya.com','')))
    return content
    
@app.route('/alltv')
def get_all_tv():
    content = ''
    content += get_douyu_content('g_yqk','斗鱼一起看')
    content += get_douyu_content('g_LOL','斗鱼LOL')

    content += get_huya_content('seeTogether','虎牙一起看')
    content += get_huya_content('lol','虎牙lol')

    
    response = make_response(content, 200)
    response.mimetype = "text/plain"
    return response


import requests
import re
import base64
import urllib.parse
import hashlib
import time


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
    l = n['wsTime']
    t = '0'
    h = '_'.join([p, t, s, f, l])
    m = hashlib.md5(h.encode('utf-8')).hexdigest()
    y = c[-1]
    url = "{}?wsSecret={}&wsTime={}&u={}&seqid={}&{}".format(i, m, l, t, f, y)
    return url


def get_real_url(room_id):
    try:
        room_url = 'https://m.huya.com/' + str(room_id)
        header = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/75.0.3770.100 Mobile Safari/537.36 '
        }
        response = requests.get(url=room_url, headers=header).text
        liveLineUrl = re.findall(r'"liveLineUrl":"([\s\S]*?)",', response)[0]
        liveline = base64.b64decode(liveLineUrl).decode('utf-8')
        if liveline:
            if 'replay' in liveline:
                return '直播录像：' + liveline
            else:
                liveline = live(liveline)
                real_url = ("https:" + liveline).replace("hls", "flv").replace("m3u8", "flv")
        else:
            real_url = '未开播或直播间不存在'
    except:
        real_url = '未开播或直播间不存在'
    return real_url


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8088)