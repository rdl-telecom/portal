import logging

from tornado.web import asynchronous
from tornado import gen

from common import CommonHandler

logger = logging.getLogger(__name__)


class PhoneHandler(CommonHandler):

    @asynchronous
    def post(self, *args, **kwargs):
        p = self.get_argument('phone_number', '')
        logger.debug('Got "phone" as {}'.format(p))
        lang = self.get_argument('lang', 'ru')
        phone = ''.join([ c for c in p if c.isdigit() ])
        logger.debug('Set phone as {}'.format(phone))
        
        if self.application.checker.is_phone(phone):
            self.user.next_step('code')
            self.application.users.update(self.user)
        self.redirect('/', status=303)