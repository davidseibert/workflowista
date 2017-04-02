from flask import Flask, request
import asyncio
import unittest
from unittest import TestCase, skipUnless, skipIf, skip
from urllib.parse import quote
import webbrowser
import json

class LoggerMixin (object):
    
    def log(self, message):
        print('{!r}: {}'.format(self, message))

    def __repr__(self):
        return "{}".format(self.__class__.__name__)

class WorkflowOutputTest(unittest.TestCase):
    def setUp(self):
        self.workflow = Workflow()
        self.output = self.workflow.run('Client')

    def test_output_is_encodable(self):
        try:
            encoded_json = json.dumps(self.output)
        except Exception as e:
            self.failureException = type(e)
            self.fail(e)

    def test_output_contents(self):
        expected = [{'greeting': 'Hello'}]
        self.assertListEqual(self.output, expected)

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
    
    async def listen(self):
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
        loop.run_until_complete(self.connection(name))
        self.log('event loop closed')
        return self.rx.output

    async def connection(self, name):
        future_response = self.schedule(self.rx.listen)
        self.log('receiver is listening; send request')
        await self.tx.send_request(name)
        self.log('sent request; waiting for response')
        await future_response
    
    def schedule(self, func):
        task = asyncio.ensure_future(func())
        return task

if __name__ == '__main__':
    server = PythonistaServer()
    output = server.run('Client')
