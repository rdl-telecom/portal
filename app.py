#!/usr/bin/python

from tornado.web import Application, StaticFileHandler
from tornado.ioloop import IOLoop
from tornado.httpserver import HTTPServer

from services.hotsoap import HotsoapRequest, HotsoapResponse

import settings

class App(Application):
    def __init__(self):
        handlers = [
            (r'/(.*)$', StaticFileHandler, {'path' : settings.STATIC_PATH, 'default_filename' : settings.INDEX_FILE}),
        ]
        Application.__init__(self, handlers)

def main():
    app = App()
    server = HTTPServer(app)
    server.listen(80)
    IOLoop.instance().start()

if __name__ == '__main__':
    main()
