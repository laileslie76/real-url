from flask import Flask,request, jsonify,redirect
from huya import HuYa
from douyu import DouYu
from youku import YouKu
app = Flask(__name__)

@app.route('/<plat>/<rid>')
def hello_world(plat,rid):
    if 'huya' == plat:
        h = HuYa(rid)
        url = h.get_real_url()['bd']
    elif 'douyu'  == plat:
        d = DouYu(rid)
        url = d.get_real_url()
    elif 'youku' == plat:
        y = YouKu(rid)
        url = y.get_real_url()
    return redirect(url, code=302)


if __name__ == '__main__':
   app.run(host='0.0.0.0',port=8088)