from http.server import BaseHTTPRequestHandler
from urllib import parse
from huya import HuYa
from douyu import DouYu
from youku import YouKu
class GetHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = parse.urlparse(self.path)
        print(parsed_path.query)
        print(parsed_path.path)
        url = ''
        if 'huya' in parsed_path.path:
            h = HuYa(parsed_path.query)
            url = h.get_real_url()['bd']
        elif 'douyu' in parsed_path.path:
            d = DouYu(parsed_path.query)
            url = d.get_real_url()
        elif 'youku' in parsed_path.path:
            y = YouKu(parsed_path.query)
            url = y.get_real_url()
        print(url)
        self.send_response(301)
        self.send_header('Location',url)
        self.end_headers()

if __name__ == '__main__':
    from http.server import HTTPServer
    server = HTTPServer(('0.0.0.0', 8088), GetHandler)
    print('Starting server, use <Ctrl-C> to stop')
    server.serve_forever()