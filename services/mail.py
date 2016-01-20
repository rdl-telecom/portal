import logging
import traceback
import smtplib
from email.mime.text import MIMEText

from tornado import gen

logger = logging.getLogger(__name__)


class Mailer(object):

    def __init__(self, server='localhost', user=None, password=None,
                 port=25, ssl=False, starttls=False, me='web@localhost'):
        logger.debug('Initializing SMTP client. SERVER: {} USERNAME: {}'.format(server, user))
        self._server = server
        self._port = port
        self._user = user
        self._password = password
        self._ssl = ssl
        self._starttls = starttls
        self._from = me

    @gen.coroutine
    def send(self, me=None, to=[], subj='', text=''):
        smtp = yield self._create_connection()
        if not smtp:
            logger.error('Unable to connect to server')
            raise gen.Return(False)

        setup_success = yield self._setup_connection(smtp)
        if not setup_success:
            logger.error('Setting up connection failed')
            raise gen.Return(False)

        message = yield self._prepare_message(me, to, subj, text)

	result = yield self._send_message(smtp, message)

        raise gen.Return(result)

    @gen.coroutine
    def _create_connection(self):
        ssl = 'YES' if self._ssl else 'NO'
        logger.debug('Connecting to {}:{} SSL: {}'.format(self._server, self._port, ssl))
        smtp = None
        try:
            if not self._ssl:
                smtp = smtplib.SMTP(self._server, self._port)
            else:
                smtp = smtplib.SMTP_SSL(self._server, self._port)
        except Exception as e:
            logger.error(e)
            logger.debug('DETAILS', exc_info=traceback.format_exc())
        raise gen.Return(smtp)

    @gen.coroutine
    def _setup_connection(self, conn):
        logger.debug('Setting up connection')
        result = False
        try:
            yield self._helo(conn)
            if self._starttls:
                yield self._tls(conn)
            if self._user:
                yield self._login(conn)
            result = True
        except Exception as e:
            logger.error(e)
            logger.debug('DETAILS', exc_info=traceback.format_exc())
        raise gen.Return(result)

    @gen.coroutine
    def _helo(self, conn):
        logger.debug('Sending EHLO. Then HELO if failed')
        conn.ehlo_or_helo_if_needed()

    @gen.coroutine
    def _tls(self, conn):
        logger.debug('Sending STARTTLS')
        conn.starttls()

    @gen.coroutine
    def _login(self, conn):
         logger.debug('Sending LOGIN')
         conn.login(self._user, self._password)

    @gen.coroutine
    def _prepare_message(self, me, to, subj, text):
        message = MIMEText(text, _charset='utf-8')
        message['From'] = me or self._from
        message['To'] = to
        message['Subject'] = subj
        raise gen.Return(message)

    @gen.coroutine
    def _send_message(self, conn, message):
        result = False
        logger.debug('Sending message\n{}'.format(message))
        try:
            conn.sendmail(message['From'], [ message['To'] ], message.as_string())
            result = True
            logger.info('Message to {} was sent'.format(message['To']))
        except Exception as e:
            logger.error(e)
            logger.debug('DETAILS', exc_info=traceback.format_exc())
        finally:
            conn.quit()
        raise gen.Return(result)
