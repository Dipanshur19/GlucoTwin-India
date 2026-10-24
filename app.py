"""Run: python app.py. Opens a private local research dashboard."""
import os
os.environ.setdefault('OMP_NUM_THREADS','2')
os.environ.setdefault('OPENBLAS_NUM_THREADS','2')
import argparse,json,pathlib,threading,webbrowser
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
from urllib.parse import urlparse,parse_qs
from glucotwin.service import TwinService,clean_json
from glucotwin.core import scenario_curve
ROOT=pathlib.Path(__file__).resolve().parent

def make_handler(service):
    class Handler(BaseHTTPRequestHandler):
        def respond(self,data,status=200,ctype='application/json'):
            payload=json.dumps(clean_json(data),allow_nan=False).encode() if ctype=='application/json' else data
            self.send_response(status);self.send_header('Content-Type',ctype);self.send_header('Content-Length',str(len(payload)))
            self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff');self.end_headers();self.wfile.write(payload)
        def do_GET(self):
            u=urlparse(self.path);q=parse_qs(u.query)
            try:
                if u.path=='/api/meta':return self.respond(service.metadata())
                if u.path=='/api/health':return self.respond({'status':'ok','version':'1.0.0'})
                if u.path=='/api/snapshot':
                    return self.respond(service.snapshot(int(q['patient'][0]),int(q['index'][0]),q.get('outage',['0'])[0]=='1',q.get('reveal',['0'])[0]=='1'))
                if u.path in ('/','/index.html'):return self.respond((ROOT/'web/index.html').read_bytes(),ctype='text/html; charset=utf-8')
                return self.respond({'error':'Not found'},404)
            except (ValueError,KeyError,IndexError) as e:return self.respond({'error':str(e)},400)
            except Exception:return self.respond({'error':'Internal error. See terminal.'},500)
        def log_message(self,format,*args):pass
    return Handler

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--port',type=int,default=8765);ap.add_argument('--no-browser',action='store_true');a=ap.parse_args()
    service=TwinService();server=ThreadingHTTPServer(('127.0.0.1',a.port),make_handler(service))
    url=f'http://127.0.0.1:{a.port}';print(f'GlucoTwin India | {url}\nResearch prototype. Press Ctrl+C to stop.',flush=True)
    if not a.no_browser:threading.Timer(1,lambda:webbrowser.open(url)).start()
    try:server.serve_forever()
    except KeyboardInterrupt:server.server_close()
