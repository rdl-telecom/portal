import logging

from tornado.web import RequestHandler, MissingArgumentError, asynchronous
from tornado import gen

logger = logging.getLogger(__name__)


class PhoneHandler(RequestHandler):

    def initialize(self):
        self.db = self.application.db
        self.auth = self.application.auth
        self.radius_realm = self.application.radius_realm

    @asynchronous
    @gen.engine
    def get(self, *args, **kwargs):
        self.ip = self.request.remote_ip
        self.mac = yield self._get_mac()

        redirect_url = self.application.urls['error']

        if self.mac:
            self.code = yield self.db.get_user_code(self.mac)
            if not self.code:
                redirect_url = self.application.urls['phone']
            else:
                self.authenticated = yield self._authenticate()
                if self.authenticated:
                    redirect_url = self.application.urls['enter']

        self.redirect(redirect_url)

    @gen.coroutine
    def _authenticate(self):
        user_info = {
            'ip' : self.ip,
            'username' : self.mac.lower(),
            'realm' : self.radius_realm,
            'password' : self.code,
            'useragent' : self.request.headers.get('User-Agent', '<Unknown>'),
            'language' : self.request.headers.get('Accept-Language', 'ru')
        }
        result = yield self.auth.login(**user_info)
        if future.exception():
            raise gen.Return(False)
        else:
            raise gen.Return(future.result())

    @gen.coroutine
    def _get_mac(self):
        mac = None
        macs = self.get_arguments('mac')
        if macs:
            mac = macs[0]
        if not mac or mac == '00:00:00:00:00:00':          # Invalid or missing MAC address in request
            with open('/proc/net/arp', 'r') as arp_file:
                for line in arp_file.readlines()[1:]:
                    (ip, _, _, mac_, _, _) = line.split()
                    if ip == self.ip:
                        mac = mac_
                        break
        raise gen.Return(mac)
