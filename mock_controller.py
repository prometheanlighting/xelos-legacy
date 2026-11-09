import http.server, sys
KNOWN={'/time','/brightness','/speed','/palette','/pattern','/gapVal','/gapFillVal','/Custom','/timer1','/activeTimer','/blend','/noblend'}
class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        p=self.path.split('?')[0]
        print(('OK  ' if p in KNOWN else 'BAD ')+self.path, flush=True)
        self.send_response(202); self.send_header('Content-Type','text/html'); self.end_headers(); self.wfile.write(b'ok')
    def log_message(self,*a): pass
http.server.ThreadingHTTPServer(('127.0.0.1',8099),H).serve_forever()
