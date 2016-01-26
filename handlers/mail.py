import logging

from tornado.web import RequestHandler, MissingArgumentError, asynchronous
from tornado.ioloop import IOLoop
from tornado import gen

logger = logging.getLogger(__name__)


class MailHandler(RequestHandler):

    @asynchronous
    @gen.engine
    def post(self, *args, **kwargs):
        job = self.application.mailer.send
        subj = 'CONTACT US from {}'.format(self.application.system_name)
        name = self.get_argument('name', default='<INCOGNITO>').encode('utf-8')
        email = self.get_argument('email', default='<NO EMAIL>').encode('utf-8')
        msg = self.get_argument('message', default='')[:10240].encode('utf-8')
        message = '{} ({}) wrote:\n\n{}\n'.format(name, email, msg)
        kwds = {
            'to' : self.application.support_email,
            'subj' : subj,
            'text' : message
        }
        self.application.run_background(self.application.mailer.send, (), kwds)

        self.redirect(self.request.headers.get('Referer', 'index.html'), status=303)
