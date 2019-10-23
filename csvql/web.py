"""Define a simple webserver for a barebones SQL dashboard."""

import time
import json

import queue

from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Dict

import logging
from logging.handlers import QueueHandler

import os
import re
from urllib.parse import unquote

from . import tokenise, parse, interpret, execute
from . import database

log = logging.getLogger(__name__)

log_queue = queue.Queue()
user_log = QueueHandler(log_queue)
user_log.setLevel("INFO")
formatter = logging.Formatter('%(levelname)s (%(module)s): %(message)s')
user_log.setFormatter(formatter)
for child in ["tokenise", "execute", "parse", "interpret"]:
    logging.root.getChild(f"csvql.{child}").addHandler(user_log)

console_log = logging.StreamHandler()
console_log.setLevel("DEBUG")
formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
console_log.setFormatter(formatter)
logging.root.getChild(f"csvql.web").addHandler(console_log)

myregex = "^" + "(?P<name>.*)" + "\.csv" + "$"

DATABASE: Dict[str, database.Table] = {}

log.info("Loading tables...")
for file in os.listdir("../data/"):
    match = re.match(myregex, file)
    if not match:
        continue
    name = match.group('name')
    if not name:
        continue
    table = database.load_table("../data/" + name + ".csv")
    if not table:
        continue
    DATABASE.update({name : table})

log.info("Loaded tables: %s", DATABASE.keys())


HOSTNAME = "localhost"
HOSTPORT = 8080

def sanitise(string: str) -> str:
    """Cleans up a http string."""
    return str(unquote(string))

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
    if obj is None:
        return obj
    if isinstance(obj, tuple):
        return varify(obj._asdict())
    if not hasattr(obj, '__dict__'):
        log.debug("Unhandled varify object %s", obj)
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
            log_queue.queue.clear()
            query = sanitise(self.path[1:])
            log.debug("Query: %s", query)
            tokens = tokenise.tokenise(query)
            log.debug("Tokens: %s", tokens)
            tree = parse.parse(tokens)
            log.debug("Tree: %s", tree)
            command = interpret.make_select(tree)
            log.debug("Command: %s", command)
            result = execute.select(command, DATABASE)
            log.debug("Result: %s", result)
            self.wfile.write(bytes(json.dumps(varify({"value" : result, "messages" : [record.getMessage() for record in list(log_queue.queue)]})), "utf-8"))
            #self.wfile.write(bytes(json.dumps(varify(parse(sanitise(self.path)))), "utf-8"))
    
    def do_POST(self) -> None:
        log.info(f"incoming https: {self.path}")
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        self.send_response(200)
        #client.close()
    def log_message(self, format, *args) -> None:
        return


def main() -> None:
    """Run the webserver."""
    MY_SERVER = HTTPServer((HOSTNAME, HOSTPORT), MyServer)

    log.info(f"Server Starts - {HOSTNAME}:{HOSTPORT}")

    try:
        MY_SERVER.serve_forever()
    except KeyboardInterrupt:
        pass

    MY_SERVER.server_close()
    log.info(f"Server Stops - {HOSTNAME}:{HOSTPORT}")
