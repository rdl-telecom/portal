import logging

from tornado.web import asynchronous
from tornado import gen

from common import CommonHandler

logger = logging.getLogger(__name__)


class CodeHandler(CommonHandler):

    @asynchronous
    @gen.engine
    def post(self, *args, **kwargs):
        c = self.get_argument('code', '')
        logger.debug('Got "code" as {}'.format(c))
        lang = self.get_argument('lang', 'ru')
        redirect_url = code
        if not self.application.checker.is_code(code):
            redirect_url = self.request.headers.get('Referer',
                                   self.application.urls['code'])
        
        redirect_url = self.application.urls['enter']
        self.redirect(redirect_url, status=303)