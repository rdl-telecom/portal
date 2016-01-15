import logging

from tornado.httpclient import HTTPClient, HTTPRequest, HTTPError
from tornado import gen
from tornado.ioloop import IOLoop

from hotsoap import HotsoapRequest, HotsoapResponse

logger = logging.getLogger(__name__)


class HotsoapClient(object):

    def __init__(self, url):
        self.url = url

    @gen.coroutine
    def send(self, method, **params):
        request = HTTPRequest(
                self.url,
                method='POST',
                headers={'Content-type' : 'application/xml', 'encoding' : 'utf-8'},
                body=str(HotsoapRequest(method, **params))
        )
        client = HTTPClient()
        logger.debug('Sending Hotsoap request: {}'.format(request.body))
        response = yield gen.Task(client.fetch, request)
	raise gen.Return(HotsoapResponse(response.body))


class Auth(object):

    def __init__(self, url):
        self._url = url
        self.hotsoap_client = HotsoapClient(url)
        logger.debug('Created Hotsoap client')

    @gen.coroutine
    def login(self, user_info):
        result = False
        response = self.hotsoap_client.send('Logon', **user_info)
	if response:
            result = response.result()['result'] == 'Success'
        if not result:
            logger.error('User {} not authenticated because {}'.format(user_info, response.result()['result']))
        else:
            logger.debug('Successfull user authentication')
        raise gen.Return(result)
