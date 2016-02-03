#!/usr/bin/python

import logging
from multiprocessing.pool import ThreadPool

from tornado.web import Application, StaticFileHandler
from tornado.ioloop import IOLoop
from tornado.httpserver import HTTPServer

from services.auth import Auth
from services.check import Checker
from services.db import DB
from services.mail import Mailer
from services.rabbit import Publisher
from services.system import get_system_name
from services.users import Users

from handlers.index import IndexHandler
from handlers.phone import PhoneHandler
from handlers.code import CodeHandler
from handlers.mail import MailHandler
from handlers.auth import AuthHandler
from handlers.lang import LangHandler

import aux
import settings

logger = logging.getLogger('main')


class App(Application):

    def __init__(self):
        logger.debug('Initializing application')

        self.radius_realm = settings.RADIUS_REALM
        self.system_name = get_system_name(settings.SYSTEM_NAME_FILE)

        self.create_hotsoap_auth_interface()
        self.create_db_connection_pool()
        self.create_mailer()
        self.create_thread_pool()
        self.create_rabbit_publisher()
        self.create_input_checker()
        self.create_users_sessions()

        self.define_urls()

        handlers = [
            (r'^/$', IndexHandler),
            (r'^/phone$', PhoneHandler),
            (r'^/code$', CodeHandler),
            (r'^/mail$', MailHandler),
            (r'^/auth$', AuthHandler),
            (r'^/lang?.*$', LangHandler),
            (r'/(.*)$', StaticFileHandler, { 'path':settings.STATIC_PATH })
        ]
        settings_dict = {
            'static_path' : settings.STATIC_PATH,
            'template_path' : settings.TEMPLATE_PATH
        }
        Application.__init__(self, handlers, **settings_dict)
        logger.debug('Application initialized')

    def create_db_connection_pool(self):
        self.db = DB(host=settings.DB_HOST, port=settings.DB_PORT,
                     user=settings.DB_USER, passwd=settings.DB_PASS,
                     db=settings.DB_NAME)

    def create_hotsoap_auth_interface(self):
        self.auth = Auth(settings.HOTSOAP_URL)

    def create_mailer(self):
        self.support_email = settings.SUPPORT_EMAIL
        self.mailer = Mailer(server=settings.MAIL_SERVER,
                             port=settings.MAIL_PORT,
                             user=settings.MAIL_USER,
                             password=settings.MAIL_PASSWORD,
                             starttls=settings.MAIL_STARTTLS,
                             ssl=settings.MAIL_SSL,
                             me=settings.MAIL_FROM)

    def create_thread_pool(self):
        self._workers = ThreadPool(settings.NUM_WORKERS)

    def create_rabbit_publisher(self):
        self.rabbit = Publisher(settings.RABBIT_URL, settings.EVENT_EXCHANGE,
                                settings.EVENT_EXCHANGE_TYPE, self.system_name,
                                settings.EVENT_ROUTING_KEY)
        self.rabbit.connect()

    def create_input_checker(self):
        self.checker = Checker()

    def create_users_sessions(self):
        self.users = Users(settings.MEMCACHE_URLS, aux.get_time(settings.SESSION_TIME))

    def define_urls(self):
        self.urls = {
            'phone' : settings.URL_PHONE,
            'code' : settings.URL_CODE,
            'enter' : settings.URL_ENTER,
            'error' : settings.URL_ERROR
        }

    def run_background(self, func, args=(), kwds={}, callback=None):
        def _callback(result):
            cb = callback or self._empty_callback
            IOLoop.current().add_callback(lambda: cb(result))
        self._workers.apply_async(func, args, kwds, _callback)

    def _empty_callback(self, res):
        logger.debug('Background task completed. RESULT = %s', str(res))


def main():
    log_level = logging.INFO
    if settings.DEBUG:
        log_level = logging.DEBUG
    logging.basicConfig(level=log_level,
                        format=settings.LOG_FORMAT,
                        datefmt=settings.LOG_DATE_FORMAT)

    db = DB(host=settings.DB_HOST, port=settings.DB_PORT,
            user=settings.DB_USER, passwd=settings.DB_PASS, db=settings.DB_NAME)


    application = App()

    server = HTTPServer(application)
    server.listen(80)
    logger.debug('Created HTTP server')
    ioloop = IOLoop.instance()

    try:
        logger.info('Starting')
        ioloop.start()
    except KeyboardInterrupt:
        logger.info('Stopping')
        ioloop.stop()


if __name__ == '__main__':
    main()
