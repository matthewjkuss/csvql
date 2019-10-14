"""Define a simple webserver for a barebones SQL dashboard."""

import time
import json

from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Dict

from tokenise import tokenise
from parse import parse, print_clause
from sql import run
import os
import re
import urllib

import database

myregex = "^" + "(?P<name>.*)" + "\.csv" + "$"

DATABASE: Dict[str, database.Table] = {}

print("Loading tables...")
for file in os.listdir("../data/"):
    match = re.match(myregex, file)
    if not match:
        continue
    name = match.group('name')
    if not name:
        continue
    table = database.load_table("../data/" + name + ".csv").value
    if not table:
        continue
    DATABASE.update({name : table})

print("Loaded tables:", DATABASE.keys())


HOSTNAME = "localhost"
HOSTPORT = 8080

def sanitise(string: str) -> str:
    """Cleans up a http string."""
    return str(urllib.parse.unquote(string))

with open('web/index.html', 'r') as html_file:
    WEB_PAGE = html_file.read()

with open('web/main.js', 'r') as js_file:
    WEB_SCRIPT = js_file.read()

with open('web/style.css', 'r') as css_file:
    WEB_STYLE = css_file.read()

def varify(obj: Any) -> Any:
    if isinstance(obj, set):
        return list(obj)
    if isinstance(obj, dict):
        for k, v in obj.items():
            obj[k] = varify(v)
        return obj
    if isinstance(obj, list):
        return obj
    if isinstance(obj, tuple):
        return varify(obj._asdict())
    if not hasattr(obj, '__dict__'):
        print("Note:", obj)
        return obj
    mapping = vars(obj)
    for key, value in mapping.items():
        mapping[key] = varify(value)
    result = mapping
    return result

class MyServer(BaseHTTPRequestHandler):
    """Just a very basic server."""
    def do_GET(self) -> None:
        self.send_response(200, "OK")
        if self.path == "/":
            self.send_header("content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(bytes(WEB_PAGE, "utf-8"))
        elif self.path == "/main.js":
            self.send_header("content-type", "text/javascript; charset=utf-8")
            self.end_headers()
            self.wfile.write(bytes(WEB_SCRIPT, "utf-8"))
        elif self.path == "/style.css":
            self.send_header("content-type", "text/css; charset=utf-8")
            self.end_headers()
            self.wfile.write(bytes(WEB_STYLE, "utf-8"))   
        else:
            print("Parsed structure:")
            print(print_clause(parse(sanitise(self.path)).value))
            print(varify(run(sanitise(self.path), DATABASE)))
            self.wfile.write(bytes(json.dumps(varify(run(sanitise(self.path), DATABASE))), "utf-8"))
            #self.wfile.write(bytes(json.dumps(varify(parse(sanitise(self.path)))), "utf-8"))
    
    def do_POST(self) -> None:
        print(f"incoming https: {self.path}")
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        self.send_response(200)
        #client.close()


def main() -> None:
    """Run the webserver."""
    MY_SERVER = HTTPServer((HOSTNAME, HOSTPORT), MyServer)

    print(time.asctime(), f"Server Starts - {HOSTNAME}:{HOSTPORT}")

    try:
        MY_SERVER.serve_forever()
    except KeyboardInterrupt:
        pass

    MY_SERVER.server_close()
    print(time.asctime(), f"Server Stops - {HOSTNAME}:{HOSTPORT}")
