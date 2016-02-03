import logging

from tornado.web import asynchronous
from tornado import gen

from common import CommonHandler

logger = logging.getLogger(__name__)


class CodeHandler(CommonHandler):

    @asynchronous
    def post(self, *args, **kwargs):
        code = self.get_argument('code', '')
        logger.debug('Got "code" as {}'.format(code))

        if self.application.checker.is_code(code):
#            if code == self.user.code:
            self.user.next_step('enter')
            self.application.users.update(self.user)
        self.redirect('/', status=303)