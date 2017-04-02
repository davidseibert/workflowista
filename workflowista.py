import asyncio
from urllib.parse import quote
import json
import pytest

from flask import Flask, request
import webbrowser

VERBOSE_PRINTING = True

class LoggerMixin (object):
    def log(self, message):
        if VERBOSE_PRINTING:
            print('{!r}: {}'.format(self, message))

    def __repr__(self):
        return "{}".format(self.__class__.__name__)

class Receiver(LoggerMixin):    
    output = []
    def __init__(self):
        super().__init__()
        self.flask = Flask(__name__)
        
        @self.flask.route('/', methods = ['POST'])
        def index():
            data = request.get_json()
            self.log('received POST request with JSON: {!r}'.format(data))
            self.output.append(data)
            shutdown = request.environ.get('werkzeug.server.shutdown')
            shutdown()
            return "<h1>Thanks!</h1><p>Shutting down now...</p>"
    
    async def start_flask(self):
        self.log('sleeping')
        await asyncio.sleep(0.1)
        self.log('done sleeping')
        self.log('flask started; ready to receive response')
        self.flask.run()
        self.log('flask ended')

class Transmitter(LoggerMixin):
    def make_url(self, name):
        SCHEME = "".join([
        "workflow://",
        "x-callback-url/",
        "run-workflow",
        "?name={}",
        "&x-success=pythonista://",
        ])
        return SCHEME.format(quote(name))

    async def send_request(self, name):
        self.log('sleeping')
        await asyncio.sleep(0.1)
        self.log('opening Workflow {!r}'.format(name))
        url = self.make_url(name)
        webbrowser.open(url)
        
        self.log('opened {!r}'.format(url))

class PythonistaServer (LoggerMixin):
    def __init__(self):
        super().__init__()
        self.rx = Receiver()
        self.tx = Transmitter()

    def run(self, name):
        self.log('preparing to run Workflow {!r}'.format(name))
        self.log('starting event loop')
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.send_and_receive(name))
        self.log('event loop closed')
        return self.rx.output

    async def send_and_receive(self, name):
        future_response = self.schedule(self.rx.start_flask)
        self.log('receiver is listening; send request')
        await self.tx.send_request(name)
        self.log('sent request; waiting for response')
        await future_response
    
    def schedule(self, func):
        task = asyncio.ensure_future(func())
        return task

def test():
    server = PythonistaServer()
    output = server.run('Client')
    expected = [{'greeting': 'Hello'}]
    assert output == expected

if __name__ == '__main__':
    server = PythonistaServer()
    output = server.run('Client')
