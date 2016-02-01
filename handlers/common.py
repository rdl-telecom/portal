import logging

from tornado.web import RequestHandler, asynchronous
from tornado import gen

logger = logging.getLogger(__name__)


class CommonHandler(RequestHandler):

    def initialize(self):
        self.ip = self.request.remote_ip
        self.user = self.application.users.get(self.ip)