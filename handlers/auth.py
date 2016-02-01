import logging

from tornado.web import asynchronous
from tornado import gen

from common import CommonHandler

logger = logging.getLogger(__name__)

    @asynchronous
    @gen.engine
    def post(self):
        user_info = {
            'ip' : self.ip,
            'username' : self.user.mac,
            'realm' : self.application.radius_realm,
            'password' : self.user.code,
            'useragent' : self.request.headers.get('User-Agent', '<Unknown>'),
            'language' : self.user.lang
        }
        success = yield self.auth.login(**user_info)
        if success:
            self.user.authorize()
            self.application.users.update(self.user)