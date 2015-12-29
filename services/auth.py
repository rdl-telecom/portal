from hotsoap import HotsoapRequest, HotsoapResponse
from tornado.httpclient import HTTPClient, HTTPRequest, HTTPError
from tornado import gen
from tornado.ioloop import IOLoop


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
        response = yield gen.Task(client.fetch, request)
	raise gen.Return(HotsoapResponse(response.body))


class Auth(object):
    def __init__(self, url):
        self._url = url
        self.hotsoap_client = HotsoapClient(url)

    @gen.coroutine
    def login(self, user_info):
        result = False
        response = self.hotsoap_client.send('Logon', **user_info)
	if response:
            result = response.result()['result'] == 'Success'
        raise gen.Return(result)
