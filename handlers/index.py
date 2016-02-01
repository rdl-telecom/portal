import logging

from tornado.web import asynchronous
from tornado import gen

from common import CommonHandler

logger = logging.getLogger(__name__)


class IndexHandler(CommonHandler):

    def initialize(self):
        CommonHandler.initialize(self)
        self.db = self.application.db

    @asynchronous
    @gen.engine
    def get(self, *args, **kwargs):
        redirect_url = yield self.next_step()
        self.redirect(redirect_url, status=303)

    @gen.coroutine
    def next_step(self):
        redirect_url = None
        if not self.user:
            redirect_url = yield self.no_session()
        else:
            redirect_url = yield self.has_session()
        raise gen.Return(redirect_url)

    @gen.coroutine
    def no_session(self):
        redirect_url = self.application.urls['error']
        code = ''
        mac = yield self._get_mac()

        if mac:
            code = yield self.db.get_user_code(mac)
            if not code:
                redirect_url = self.application.urls['phone']
                code = ''
            else:
                redirect_url = self.application.urls['enter']

            self.application.users.add(self.ip, mac, code)
        raise gen.Return(redirect_url)

    @gen.coroutine
    def has_session(self):
        redirect_url = None
        if self.user.phone:
            if self.user.code:
                redirect_url = self.application.urls['enter']
            else:
                redirect_url = self.application.urls['code']
        else:
            redirect_url = self.application.urls['phone']
        raise gen.Return(redirect_url)

    @gen.coroutine
    def _get_mac(self):
        mac = None
        with open('/proc/net/arp', 'r') as arp_file:
            for line in arp_file.readlines()[1:]:
                (ip, _, _, tmp_mac, _, _) = line.split()
                if ip == self.ip:
                    mac = tmp_mac
                    break
        raise gen.Return(mac)
