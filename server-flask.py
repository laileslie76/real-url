from flask import Flask,request, jsonify,redirect,make_response
from douyu import DouYu
from youku import YouKu
from bs4 import BeautifulSoup
from expiringdict import ExpiringDict
import requests,base64,json
import io
import sys
import re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf8')

app = Flask(__name__)
url=''
cache = ExpiringDict(max_len=100, max_age_seconds=300)
@app.route('/<plat>/<rid>')
def get_url(plat,rid):
    if 'huya' == plat:
        # h = HuYa(rid)
        url = get_real_url(rid)
    elif 'douyu'  == plat:
        d = DouYu(rid)
        url = d.get_real_url()['2000p']
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
                content += ('{},http://oracle.lppsuixn.tk:8088/douyu{}\n'.format(get_nick(litag.find('div',{'class','DyListCover-userName'}))  + litag.find('h3',{'class','DyListCover-intro'}).text,litag.find('a', href=True)['href']))
    return content

def get_huya_content(group,name):
    content=name+',#genre#\n'
    url ='https://www.huya.com/g/' + group
    text = requests.get(url).text
    soup = BeautifulSoup(text, 'html.parser')
    for ultag  in soup.find_all('ul', {'class': 'live-list clearfix'}):
         for litag in ultag.find_all('li'):
            if litag:
                content += ('{},http://oracle.lppsuixn.tk:8088/huya{}\n'.format(get_nick(litag.find('i',{'class','nick'})) + litag.find('a',{'class','title'}).text,litag.find('a',{'class','title'}, href=True)['href'].replace('https://www.huya.com','')))
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

def get_douyu_content_json(group,name):
    data = {'group':name,'channels':[]}
    url ='https://www.douyu.com/' + group
    text = requests.get(url).text
    soup = BeautifulSoup(text, 'html.parser')
    for ultag  in soup.find_all('ul', {'class': 'layout-Cover-list'}):
         for litag in ultag.find_all('li'):
            if litag:
                item={
                    'name':get_nick(litag.find('div',{'class','DyListCover-userName'}))  + litag.find('h3',{'class','DyListCover-intro'}).text,
                    'urls':[]
                }
                item['urls'].append('http://oracle.lppsuixn.tk:8088/douyu{}'.format(litag.find('a', href=True)['href']))
                data['channels'].append(item)
    return data

def get_huya_content_json(group,name):
    data = {'group':name,'channels':[]}
    url ='https://www.huya.com/g/' + group
    text = requests.get(url).text
    soup = BeautifulSoup(text, 'html.parser')
    for ultag  in soup.find_all('ul', {'class': 'live-list clearfix'}):
         for litag in ultag.find_all('li'):
            if litag:
                item={
                    'name':get_nick(litag.find('i',{'class','nick'})) + litag.find('a',{'class','title'}).text,
                    'urls':[]
                }
                item['urls'].append('http://oracle.lppsuixn.tk:8088/huya{}'.format(litag.find('a',{'class','title'}, href=True)['href'].replace('https://www.huya.com','')))
                # if len(data['channels']) > 5:
                #     continue
                data['channels'].append(item)
    return data

def get_iptv_json(url,name):
    data = {'group':name,'channels':[]}
    text = requests.get(url,headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}).text
    channel_map = {}
    for line in text.split():
        n,u = line.split(',')
        if n not in channel_map:
            channel_map[n] = {
                'name':n,
                'urls':[]
            }
        channel_map[n]['urls'].append(u)
    for k,v in channel_map.items():
        data['channels'].append(v)
    return data
@app.route('/maotv')
def get_mao_tv():
    with open("/tv/ts.json", encoding='utf-8') as f:
        data = json.load(f)
        data['lives'] = []
        data['lives'].append(get_iptv_json('https://cdn.jsdelivr.net/gh/lppsuixn/myiptv@latest/utf8/groups/cctv-simple.txt','央视'))
        data['lives'].append(get_iptv_json('https://cdn.jsdelivr.net/gh/lppsuixn/myiptv@latest/utf8/groups/weishi-simple.txt','卫视'))
        data['lives'].append(get_iptv_json('https://cdn.jsdelivr.net/gh/lppsuixn/myiptv@latest/utf8/groups/difang-simple.txt','地方'))
        data['lives'].append(get_iptv_json('https://cdn.jsdelivr.net/gh/lppsuixn/myiptv@latest/utf8/groups/special-simple.txt','特殊'))
        data['lives'].append(get_douyu_content_json('g_yqk','斗鱼一起看'))
        data['lives'].append(get_douyu_content_json('g_LOL','斗鱼LOL'))
        data['lives'].append(get_huya_content_json('seeTogether','虎牙一起看'))
        data['lives'].append(get_huya_content_json('lol','虎牙lol'))


        response = make_response(jsonify(data), 200)
        response.mimetype = "text/plain"
        return response
@app.route('/v2ml809')
def v2ml809_convert():
    sub_url = request.args['sub_url']
    return_content = requests.get(sub_url,headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}).content
    if (len(return_content) % 3 == 1):
        return_content += b"="
    elif (len(return_content) % 3 == 2):
        return_content += b"=="
    print(return_content)
    base64Str = base64.urlsafe_b64decode(return_content)  # 进行base64解码
    print("解码后内容：", base64Str)
    share_links = base64Str.splitlines()  # \r\n进行分行
    add = ""

    for share_link in share_links:
        dict = {}
        share_link = bytes.decode(share_link)  # 转换类型
        if share_link.find("vmess://") == -1:
                # print("")
               # vmesscode = "抱歉，您的订阅链接不是vmess链接。"
            pass
        else:
            print("服务器参数：", share_link)
            shar = share_link.split("ss://")
            jj = base64.urlsafe_b64decode(shar[1]).decode('UTF-8')  # 解析VMESS参数得到josn字符串 后面解析unicode
                # jj = base64.urlsafe_b64decode(shar[1]) # 解析VMESS参数得到josn字符串 后面解析unicode
            print("vmess参数解析得到josn内容：",jj)

            par = json.loads(jj)  # 转换成字典
            if par['port'] != '809':
                continue   
            if '华南' in par['ps']:
                par['ps'] = '华南'
            if '华中' in par['ps']:
                par['ps'] = '华中'
            add = add + vm(par,par['host'])
    dic3 = base64.b64encode(add.encode('UTF-8'))
    vmesscode = dic3
    print("订阅内容：")
    print(dic3)
    response = make_response(dic3, 200)
    response.mimetype = "text/plain"
    return response


@app.route('/v2ml')
def v2ml_convert():
    sub_url = request.args['sub_url']
    hostname = request.args['hostname']
    return_content = requests.get(sub_url,headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}).content
    if (len(return_content) % 3 == 1):
        return_content += b"="
    elif (len(return_content) % 3 == 2):
        return_content += b"=="
    print(return_content)
    base64Str = base64.urlsafe_b64decode(return_content)  # 进行base64解码
    print("解码后内容：", base64Str)
    # print(sub_url)



    share_links = base64Str.splitlines()  # \r\n进行分行
    add = ""

    for share_link in share_links:
        dict = {}
        share_link = bytes.decode(share_link)  # 转换类型
        if share_link.find("vmess://") == -1:
                # print("")
               # vmesscode = "抱歉，您的订阅链接不是vmess链接。"
            pass
        else:
            print("服务器参数：", share_link)
            shar = share_link.split("ss://")
            jj = base64.urlsafe_b64decode(shar[1]).decode('UTF-8')  # 解析VMESS参数得到josn字符串 后面解析unicode
                # jj = base64.urlsafe_b64decode(shar[1]) # 解析VMESS参数得到josn字符串 后面解析unicode
            print("vmess参数解析得到josn内容：",jj)

            par = json.loads(jj)  # 转换成字典
            if par['port'] != '80':
                continue
            if 'network' in par and par['network'] != 'ws':
                continue
            if 'net' in par and par['net'] != 'ws':
                continue
            #if 'path' in par:
            #    par['path']='/index'
            add = add + vm(par,hostname)
    dic3 = base64.b64encode(add.encode('UTF-8'))
    vmesscode = dic3
    print("订阅内容：")
    print(dic3)
    response = make_response(dic3, 200)
    response.mimetype = "text/plain"
    return response



def vm(par,hostname):
    par["host"] = hostname
    dic = json.dumps(par)  # 转换成json
    dic1 = base64.b64encode(dic.encode('UTF-8'))  # 转换成base64字符串
    dic2 = 'vmess://' + bytes.decode(dic1) + "\r\n"  # 拼接vmess头
    return dic2

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
    app.config['JSON_AS_ASCII'] = False
    app.run(host='0.0.0.0',port=8088)
