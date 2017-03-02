from flask import Flask, request
import asyncio
from urllib.parse import quote
import webbrowser
import logging

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

def logged(func):
    def newfunc(*args, **kwargs):
        log.debug('entering {}: args={}, kwargs={}'.format(func.__name__, args, kwargs))
        res = func(*args, **kwargs)
        log.debug('leaving {}'.format(func.__name__))
        return res
    return newfunc

def sleep(func):
    async def newfunc(*args, **kwargs):
        log.debug('sleeping in {}'.format(func.__name__))
        await asyncio.sleep(0.1)
        log.debug('done sleeping in {}'.format(func.__name__))
        res = logged(func)(*args, **kwargs)
        return res
    return newfunc


class Workflow (object):
    SCHEME = "workflow://x-callback-url/run-workflow?name={}&x-success=pythonista://"
    def __init__(self, name):
        self.name = name
        self.data = []
        self.receiver = Flask(__name__)
        
        @self.receiver.route('/', methods = ['POST'])
        @logged
        def index():
            self.data.append(request.get_json())
            shutdown = logged(request.environ.get('werkzeug.server.shutdown'))
            shutdown()
            return "<h1>Thanks!</h1><p>Shutting down now...</p>"
        
    @property
    def url(self):
        return self.SCHEME.format(quote(self.name))
        
    def __repr__(self):
        return "Workflow({})".format(repr(self.name))

    @logged
    def run(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.main())
        return self.data
    
    @logged
    async def main(self):
        response = asyncio.ensure_future(self.get_response())
        await self.send_request()
        await response

    @sleep
    def get_response(self):        
        self.receiver.run()

    @sleep
    def send_request(self):
        webbrowser.open(self.url)

if __name__ == "__main__":
    workflow = Workflow("Client")
    data = workflow.run()
    log.info(data)
