import logging

from tornado import gen
from tornado_mysql.pools import Pool

logger = logging.getLogger(__name__)

def adopt_mac(mac):
    return mac.replace(':','').upper()


class DB(object):
    def __init__(self, host='127.0.0.1', port=3306, user='root', passwd='', db='mysql'):
        self.pool = Pool(dict(host=host, port=port, user=user, passwd=passwd, db=db),
                            max_idle_connections=3,
                            max_recycle_sec=3,
                            max_open_connections=20)
        logger.debug('Created database connection pool')

    @gen.coroutine
    def _query(self, query, fetchone=False, fetchall=False):
        logger.debug('QUERY: {}'.format(query))
        try:
            cur = yield self.pool.execute(query)
        except Exception as e:
            raise gen.Return(e)
        if cur:
            if fetchone:
                if cur.rowcount != 1:
                    raise gen.Return(None)
                result = cur.fetchone()
                logger.debug('RESULT: {}'.format(result))
                raise gen.Return(result)
            elif fetchall:
                result = cur.fetchall()
                logger.debug('RESULT: {}'.format(result))
                raise gen.Return(cur.fetchall())
        raise gen.Return(None)

    @gen.coroutine
    def get_user_code(self, mac):
        logger.info('Trying to find user code for MAC {}'.format(mac))
        res = yield self._query(
                  "SELECT code FROM device_code WHERE mac='{}';".format(adopt_mac(mac)),
                  fetchone=True)
        if res and not res.exception():
            (code, ) = res
            logger.info('Found code {}'.format(code))
            raise gen.Return(code)
        logger.info('Code not found')

    @gen.coroutine
    def add_user(self, mac, code):
        logger.info('Adding new user. MAC: {}, CODE: {}'.format(mac, code))
        res = yield self._query(
                  "INSERT INTO device_code (mac, code) VALUES ('{}', '{}')".format(adopt_mac(mac), code))
        if res:
            logger.debug(res)
            raise gen.Return(False)
        logger.info('Successfully added user MAC: {}, CODE: {}'.format(mac, code))
        raise gen.Return(True)
