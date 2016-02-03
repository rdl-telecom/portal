import logging

from tornado.web import asynchronous
from tornado import gen
from tornado import escape

from common import CommonHandler

logger = logging.getLogger(__name__)


class LangHandler(CommonHandler):

    @asynchronous
    @gen.engine
    def get(self, *args, **kwargs):
        self.post(*args, **kwargs)

    @asynchronous
    @gen.engine
    def post(self, *args, **kwargs):
        lang = self.get_argument('lang', 'ru')

        self.user.update_lang(lang)
        self.application.users.update(self.user)

        self.redirect('/', status=303)
