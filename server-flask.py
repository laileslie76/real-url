from flask import Flask,request, jsonify,redirect,make_response
from huya import HuYa
from douyu import DouYu
from youku import YouKu
app = Flask(__name__)

@app.route('/<plat>/<rid>')
def get_url(plat,rid):
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
    
@app.route('/alltv')
def get_all_tv():
    content = ''
    d = DouYu(1)
    content += d.get_yqk_content()

    h = HuYa(1)
    content += h.get_yqk_content()

    
    response = make_response(content, 200)
    response.mimetype = "text/plain"
    return response



if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8088)