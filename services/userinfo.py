import logging
import json

import memcache

logger = logging.getLoger(__name__)


class UserInfo(object):

    def __init__(self, urls_list, session_time):
        self.memcache = memcache.Client(urls_list)
        self.session_time = session_time

    def get(self, ip):
        result = self.memcache.get(ip)
        if result:
            result = json.load(result)
        return result

    def set(self, ip, user_info):
        self.memcache.set(ip, json.dumps(user_info), self.session_time)

    def delete(self, ip):
        self.memcache.delete(ip)
