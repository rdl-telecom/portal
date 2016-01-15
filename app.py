#!/usr/bin/python

import logging

from tornado.web import Application, StaticFileHandler
from tornado.ioloop import IOLoop
from tornado.httpserver import HTTPServer

from services.auth import Auth
from services.db import DB
from handlers.auth import AuthHandler

from dbconsumer import DatabaseConsumer
import settings

logger = logging.getLogger('main')


class App(Application):
    def __init__(self, db):
        logger.debug('Initializing application')
        self.db = db
        self.auth = Auth(settings.HOTSOAP_URL)
        self.radius_realm = settings.RADIUS_REALM
        handlers = [
            (r'^/$', AuthHandler),
            (r'/(.*)$', StaticFileHandler, {'path':settings.STATIC_PATH}),
            (r'^/authenticate$', AuthHandler)
        ]
        Application.__init__(self, handlers)


def main():
    log_level = logging.INFO
    if settings.DEBUG:
        log_level = logging.DEBUG
    logging.basicConfig(level=log_level,
                        format=settings.LOG_FORMAT,
                        datefmt=settings.LOG_DATE_FORMAT)

    db = DB(host=settings.DB_HOST, port=settings.DB_PORT,
            user=settings.DB_USER, passwd=settings.DB_PASS, db=settings.DB_NAME)

    consumer = DatabaseConsumer(db)
    application = App(db)

    server = HTTPServer(application)
    server.listen(80)
    logger.debug('Created HTTP server')
    ioloop = IOLoop.instance()
    consumer.connect(ioloop)
    try:
        logger.info('Starting main loop')
        ioloop.start()
    except KeyboardInterrupt:
        logger.info('Stopping')
        ioloop.stop()

if __name__ == '__main__':
    main()
