import os
import json
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from http.server import BaseHTTPRequestHandler

API_KEY = os.environ.get("ptlc_SfwGdnatOeFIQc6R7nNvDkZvmXIwH4EkGVhHyDVucHm", "")
SERVER_ID = os.environ.get("SERVER_ID", "5ba25eae")
PANEL_URL = f"https://panel.play.hosting/api/client/servers/{SERVER_ID}/power"

HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <title>Server Control</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; background: #121212; color: white; margin: 0; }
        .card { text-align: center; background: #1e1e1e; padding: 30px; border-radius: 12px; width: 85%; max-width: 320px; }
        .btn { border: none; padding: 15px; font-size: 16px; font-weight: bold; border-radius: 8px; cursor: pointer; color: white; width: 100%; margin-top: 15px; }
        .btn-start { background: #28a745; }
        .btn-stop { background: #dc3545; }
        .btn-restart { background: #ffc107; color: black; }
    </style>
</head>
<body>
    <div class="card">
        <h2>Minecraft Server</h2>
        <form action="/api?signal=start" method="post"><button type="submit" class="btn btn-start">Start / Wake</button></form>
        <form action="/api?signal=restart" method="post"><button type="submit" class="btn btn-restart">Restart</button></form>
        <form action="/api?signal=stop" method="post"><button type="submit" class="btn btn-stop">Stop</button></form>
    </div>
</body>
</html>"""

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(HTML_TEMPLATE.encode('utf-8'))

    def do_POST(self):
        signal = "start"
        if "signal=" in self.path:
            signal = self.path.split("signal=")[-1]

        payload = json.dumps({"signal": signal}).encode('utf-8')
        req = Request(PANEL_URL, data=payload, method="POST")
        
        # Full Browser Spoofing Headers
        req.add_header("Authorization", f"Bearer {API_KEY}")
        req.add_header("Content-Type", "application/json")
        req.add_header("Accept", "application/json")
        req.add_header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        req.add_header("Origin", "https://panel.play.hosting")
        req.add_header("Referer", f"https://panel.play.hosting/server/{SERVER_ID}")

        try:
            with urlopen(req, timeout=10) as response:
                status = response.status
                body = response.read().decode('utf-8')
        except HTTPError as e:
            status = e.code
            body = e.read().decode('utf-8')
        except URLError as e:
            status = 500
            body = str(e.reason)

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        if status in [200, 204]:
            msg = f"<h3>Successfully sent '{signal}' signal!</h3><a href='/'>Go Back</a>"
        else:
            msg = f"<h3>Error {status}</h3><p>{body}</p><a href='/'>Go Back</a>"
            
        self.wfile.write(msg.encode('utf-8'))
