import logging

from tornado.web import asynchronous
from tornado import gen
from tornado import escape

from common import CommonHandler

logger = logging.getLogger(__name__)


class IndexHandler(CommonHandler):

    def initialize(self):
        CommonHandler.initialize(self)
        self.db = self.application.db

    @asynchronous
    @gen.engine
    def get(self, *args, **kwargs):
        if not self.user:
            next_step = yield self.no_session()
        else:
            next_step = self.user.step
        self.render(self.application.urls[next_step], user=self.user)

    @gen.coroutine
    def no_session(self):
        next_step = 'error'
        code = ''
        mac = yield self._get_mac()

        if mac:
            code = yield self.db.get_user_code(mac)
            if not code:
                next_step = 'phone'
                code = ''
            else:
                next_step = 'enter'
            self.user = self.application.users.add(self.ip, mac, code=code, step=next_step)

        raise gen.Return(next_step)

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
