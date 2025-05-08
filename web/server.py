from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import os

class GameHandler(SimpleHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
    def do_POST(self):
        if self.path == '/save-highscore':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            score_data = json.loads(post_data.decode('utf-8'))
            
            # Save the high score to file
            with open('web_highscore.txt', 'w') as f:
                f.write(str(score_data['score']))
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'ok'}).encode('utf-8'))
            return

    def do_GET(self):
        if self.path == '/get-highscore':
            try:
                with open('web_highscore.txt', 'r') as f:
                    score = f.read().strip()
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'score': int(score)}).encode('utf-8'))
                return
            except:
                # If file doesn't exist or other error, return 0
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'score': 0}).encode('utf-8'))
                return
        elif self.path == '/':
            self.path = '/index.html'
        return SimpleHTTPRequestHandler.do_GET(self)

if __name__ == '__main__':
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, GameHandler)
    print('Server running on port 8000...')
    httpd.serve_forever()