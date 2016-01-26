import logging
import json

from tornado import gen

from pika.adapters import TornadoConnection
from pika import URLParameters, BasicProperties

logger = logging.getLogger(__name__)


class Agent(object):

    def __init__(self, amqp_url, exchange, type, queue, routing_key):
        self._connection = None
        self._channel = None
        self._url = amqp_url
        self._exchange = exchange
        self._exchange_type = type
        self._queue = queue
        self._routing_key = routing_key
        self._closing = False

    def connect(self, ioloop=None, stop_ioloop=True):
        logger.debug('Connecting to %s', self._url)
        self.stop_ioloop = stop_ioloop
        return TornadoConnection(URLParameters(self._url),
                                 self.on_connection_open,
                                 custom_ioloop=ioloop)

    def close_connection(self):
        logger.debug('Closing connection')
        self._connection.close()

    def add_on_connection_close_callback(self):
        logger.debug('Adding connection close callback')
        print self._connection
        self._connection.add_on_close_callback(self.on_connection_closed)

    def on_connection_closed(self, connection, reply_code, reply_text):
        self._channel = None
        if self._closing and self.stop_ioloop:
            logger.debug('Stoping tornado IOLoop')
            self._connection.ioloop.stop()
        else:
            logger.warning('Connection closed, reopening in 5 seconds: (%s) %s',
                           reply_code, reply_text)
            self._connection.add_timeout(5, self.reconnect)

    def on_connection_open(self, connection):
        logger.info('Connection opened {}'.format(connection))
        self._connection = connection
        self.add_on_connection_close_callback()
        self.open_channel()

    def open_channel(self):
        logger.debug('Creating a new channel')
        self._connection.channel(on_open_callback=self.on_channel_open)

    def reconnect(self):
        if not self._closing:
            self._connection = self.connect()

    def add_on_channel_close_callback(self):
        logger.debug('Adding channel close callback')
        self._channel.add_on_close_callback(self.on_channel_closed)

    def on_channel_closed(self, channel, reply_code, reply_text):
        logger.warning('Channel %i was closed: (%s) %s',
                       channel, reply_code, reply_text)
        self._connection.close()

    def on_channel_open(self, channel):
        logger.debug('Channel opened')
        self._channel = channel
        self.add_on_channel_close_callback()
        self.setup_exchange(self._exchange)

    def setup_exchange(self, exchange_name):
        logger.debug('Declaring exchange %s', exchange_name)
        self._channel.exchange_declare(self.on_exchange_declareok,
                                       exchange_name,
                                       self._exchange_type)

    def on_exchange_declareok(self, unused_frame):
        logger.debug('Exchange declared')
        self.setup_queue(self._queue)

    def setup_queue(self, queue_name):
        logger.debug('Declaring queue %s', queue_name)
        self._channel.queue_declare(self.on_queue_declareok, queue_name)

    def on_queue_declareok(self, method_frame):
        logger.debug('Binding "%s" to "%s" with "%s" routing key',
                    self._exchange, self._queue, self._routing_key)
        self._channel.queue_bind(self.on_bindok, self._queue,
                                 self._exchange, self._routing_key)

    def on_bindok(self, unused_frame):
        logger.info('Queue bound')

    def close_channel(self):
        logger.debug('Closing the channel')
        self._channel.close()

    def run(self, ioloop=None):
        self._connection = self.connect(ioloop)
        self._connection.ioloop.start()

    def stop(self):
        logger.info('Stopping')
        self._closing = True
        self.stop_consuming()
        logger.info('Stopped')


class Consumer(Agent):

    def __init__(self, amqp_url, exchange, type, queue, routing_key):
        Agent.__init__(self, amqp_url, exchange, type, queue, routing_key)
        self._consumer_tag = None

    def add_on_cancel_callback(self):
        logger.debug('Adding consumer cancellation callback')
        self._channel.add_on_cancel_callback(self.on_consumer_cancelled)

    def on_consumer_cancelled(self, method_frame):
        logger.debug('Consumer was cancelled remotely, shutting down: %r',
                    method_frame)
        if self._channel:
            self._channel.close()

    def acknowledge_message(self, delivery_tag):
        logger.info('Acknowledging message %s', delivery_tag)
        self._channel.basic_ack(delivery_tag)

    def on_message(self, unused_channel, basic_deliver, properties, body):
        logger.info('Received message # %s from %s: %s',
                    basic_deliver.delivery_tag, properties.app_id, body)
        self.acknowledge_message(basic_deliver.delivery_tag)

    def on_cancelok(self, unused_frame):
        logger.debug('RabbitMQ acknowledged the cancellation of the consumer')
        self.close_channel()

    def stop_consuming(self):
        if self._channel:
            logger.debug('Sending a Basic.Cancel RPC command to RabbitMQ')
            self._channel.basic_cancel(self.on_cancelok, self._consumer_tag)

    def start_consuming(self):
        logger.debug('Issuing consumer related RPC commands')
        self.add_on_cancel_callback()
        self._consumer_tag = self._channel.basic_consume(self.on_message,
                                                         self._queue)

    def on_bindok(self, unused_frame):
        logger.info('Queue bound')
        self.start_consuming()

    def open_channel(self):
        logger.debug('Opening a new channel')
        self._connection.channel(on_open_callback=self.on_channel_open)

    def run(self):
        self._connection = self.connect()
        self._connection.ioloop.start()

    def stop(self):
        logger.info('Stopping')
        self._closing = True
        logger.info('Stopped')


class Publisher(Agent):

    def __init__(self, amqp_url, exchange, type, queue, routing_key,
                 app_id='rabbit-publisher', interval=1):
        Agent.__init__(self, amqp_url, exchange, type, queue, routing_key)
        self._stopping = False
        self._interval = interval
        self._app_id = app_id

    def on_bindok(self, unused_frame):
        logger.info('Queue bound')
        self.start_publishing()

    def start_publishing(self):
        logger.debug('Issuing consumer related RPC commands')
        self.enable_delivery_confirmations()

    def enable_delivery_confirmations(self):
        logger.debug('Issuing Confirm.Select RPC command')
        self._channel.confirm_delivery(self.on_delivery_confirmation)

    def on_delivery_confirmation(self, method_frame):
        confirmation_type = method_frame.method.NAME.split('.')[1].lower()
        logger.debug('Received %s for delivery tag: %i',
                    confirmation_type,
                    method_frame.method.delivery_tag)

    def publish(self, message, content_type='application/json'):
        if self._stopping:
            return
        properties = BasicProperties(app_id=self._app_id,
                                     content_type=content_type,
#                                     headers=message,
                                     delivery_mode=1)

        if content_type == 'application/json':
            msg = json.dumps(message, ensure_ascii=False)
        else:
            msg = message

        self._channel.basic_publish(exchange=self._exchange,
                                    routing_key=self._routing_key,
                                    body=msg, properties=properties)
        logger.info('Published message %s', str(msg))

    def stop(self):
        logger.info('Stopping')
        self._stopping = True
        self.close_channel()
        logger.info('Stopped')
