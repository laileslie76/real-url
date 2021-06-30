from flask import Flask,request, jsonify,redirect,make_response
from huya import HuYa
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
        h = HuYa(rid)
        url = h.get_real_url()
        if rid in cache:
            cache[rid] +=1 
        else:
            cache[rid] = 0
        item =  cache[rid] % 4
        if item == 0:
            url = url['flv_2m']
        if item == 1:
            url = url['hls_2m']
        if item == 2:
            url = url['flv']
        if item == 3:
            url = url['hls']
    elif 'douyu'  == plat:
        d = DouYu(rid)
        url = d.get_real_url()
    elif 'youku' == plat:
        y = YouKu(rid)
        url = y.get_real_url()
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



if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8088)