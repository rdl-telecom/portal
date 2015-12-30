from tornado import gen
from tornado_mysql.pools import Pool

def adopt_mac(mac):
    return mac.replace(':','').upper()


class DB(object):
    def __init__(self, host='127.0.0.1', port=3306, user='root', passwd='', db='mysql'):
        self.pool = Pool(dict(host=host, port=port, user=user, passwd=passwd, db=db),
                            max_idle_connections=3,
                            max_recycle_sec=3,
                            max_open_connections=20
                        )

    @gen.coroutine
    def _query(self, query, fetchone=False, fetchall=False):
        cur = yield self.pool.execute(query)
        if cur:
            if fetchone:
                if cur.rowcount != 1:
                    raise gen.Return(None)
                raise gen.Return(cur.fetchone())
            elif fetchall:
                raise gen.Return(cur.fetchall())
        raise gen.Return(None)

    @gen.coroutine
    def get_user_code(self, mac):
        res = yield self._query(
                  "SELECT code FROM device_code WHERE mac='{}';".format(adopt_mac(mac)),
                  fetchone=True
              )
        if res:
            (code, ) = res
            raise gen.Return(code)

    @gen.coroutine
    def add_user(self, mac, code):
        res = yield self._query(
                  "INSERT IMTO device_code (mac, code) VALUES ('{}s', '{}s')".format(adopt_mac(mac), code)
              )
        if res.exception():
            gen.Return(False)
        gen.Return(True)
