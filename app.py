#!/usr/bin/python

from tornado.web import Application, StaticFileHandler
from tornado.ioloop import IOLoop
from tornado.httpserver import HTTPServer

from services.auth import Auth
from services.db import DB
from handlers.auth import AuthHandler
import settings


class App(Application):
    def __init__(self):
        self.db = DB(host=settings.DB_HOST,
                     port=settings.DB_PORT,
                     user=settings.DB_USER,
                     passwd=settings.DB_PASS,
                     db=settings.DB_NAME
                  )
        self.auth = Auth(settings.HOTSOAP_URL)
        self.radius_realm = settings.RADIUS_REALM
        handlers = [
            (r'^/$', AuthHandler),
            (r'/(.*)$', StaticFileHandler, {'path':settings.STATIC_PATH}),
            (r'^/authenticate$', AuthHandler)
        ]
        Application.__init__(self, handlers)


def main():
    application = App()
    server = HTTPServer(application)
    server.listen(80)
    IOLoop.instance().start()

if __name__ == '__main__':
    main()
