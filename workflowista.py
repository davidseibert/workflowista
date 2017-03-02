from flask import Flask, request
import asyncio
import unittest
from unittest import TestCase, skipUnless, skipIf, skip
from urllib.parse import quote
import webbrowser
import logging
import json

werkzeug_log = logging.getLogger('werkzeug')
werkzeug_log.setLevel(logging.DEBUG)

class LoggerMixin (object):
    def __init__(self):
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(logging.DEBUG)
        
    def __repr__(self):
        return "{}()".format(self.__class__.__name__)

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
            
            self.log.info(' -- received POST request')
            self.output.append(request.get_json())
            shutdown = request.environ.get('werkzeug.server.shutdown')
            shutdown()
            return "<h1>Thanks!</h1><p>Shutting down now...</p>"
    
    async def listen(self):
        self.log.info('sleeping')
        await asyncio.sleep(0.1)
        self.log.info('started listening')
        self.flask.run()
        self.log.info('stopped listening')

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
        self.log.info('sleeping')
        await asyncio.sleep(0.1)
        self.log.info('sending')
        webbrowser.open(self.make_url(name))
        self.log.info('sent')

class Workflow (LoggerMixin):
    def __init__(self):
        super().__init__()
        self.rx = Receiver()
        self.tx = Transmitter()

    def run(self, name):
        self.log.info('running {}'.format(repr(name)))
        self.log.info('loop starting')
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.connection(name))
        self.log.info('loop finished')
        self.log.info('received output: {}'.format(type(self.rx.output)))
        return self.rx.output

    async def connection(self, name):
        future_response = self.schedule(self.rx.listen)
        self.log.info('waiting for request')
        await self.tx.send_request(name)
        self.log.info('waiting for response')
        await future_response
    
    def schedule(self, func):
        task = asyncio.ensure_future(func())
        return task

if __name__ == '__main__':
    workflow = Workflow()
    output = workflow.run('Client')

