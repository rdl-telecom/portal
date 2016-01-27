import logging

from tornado.web import RequestHandler, MissingArgumentError, asynchronous
from tornado import gen

from utility import convert_url

logger = logging.getLogger(__name__)


class CodeHandler(RequestHandler):

    def initialize(self):
        pass

    @asynchronous
    @gen.engine
    def post(self, *args, **kwargs):
        p = self.get_argument('phone_number', '')
        logger.debug('Got "phone" as {}'.format(p))
        lang = self.get_argument('lang', 'ru')
        phone = ''.join([ c for c in p if c.isdigit() ])
        logger.debug('Set phone as {}'.format(phone))
        
        redirect_url = self.application.urls['code']
        if not self.application.checker.is_phone(phone):
            redirect_url = self.request.headers.get('Referer',
                                   convert_url(self.application.urls['phone'], lang))
        self.redirect(redirect_url, status=303)