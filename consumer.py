#!/usr/bin/python

import sys
import os

sys.path.append(os.path.dirname(__file__))

import logging
import json

from tornado.ioloop import IOLoop

from services.db import DB
from services.rabbit import Consumer
from services.system import get_system_name
import settings

logger = logging.getLogger(__name__)


class DatabaseConsumer(Consumer):

    def __init__(self, db):
        logger.info('Initializing database consumer')
        self._db = db
        self._system_name = get_system_name(settings.SYSTEM_NAME_FILE)
        logger.debug('System name: {}'.format(self._system_name))
        Consumer.__init__(self, settings.RABBIT_URL, settings.MACS_EXCHANGE,
                          settings.MACS_EXCHANGE_TYPE,
                          self._system_name, '')

    def on_message(self, unused_channel, basic_deliver, properties, body):
        logger.info('Received message # %s from %s: %s',
                    basic_deliver.delivery_tag, properties.app_id, body)
        (mac, code) = json.loads(body)
        self._db.add_user(mac, code)
        self.acknowledge_message(basic_deliver.delivery_tag)


def main():
    logging.basicConfig(level=logging.DEBUG,
                        format=settings.LOG_FORMAT,
                        datefmt=settings.LOG_DATE_FORMAT)

    db = DB(host=settings.DB_HOST, port=settings.DB_PORT,
            user=settings.DB_USER, passwd=settings.DB_PASS, db=settings.DB_NAME)
    consumer = DatabaseConsumer(db)

    try:
        consumer.run()
    except KeyboardInterrupt:
        consumer.stop()

if __name__ == '__main__':
    main()
