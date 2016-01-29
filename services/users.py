import logging
import json

import memcache

logger = logging.getLogger(__name__)


class User(object):

    def __init__(self, ip, mac, url='/index.html', lang='ru',
                       code='', mail_count=0, authorized=False):
        logger.debug('Creating user object IP={} MAC={}'.format(ip, mac))
        self.ip = ip
        self.mac = mac
        self.url = url
        self.lang = lang
        self.code = code
        self.mail_count = mail_count
        self.authorized = authorized

    @staticmethod
    def from_json(user_json):
        user_dict = json.loads(user_json)
        return User(**user_dict)

    def update_lang(self, lang):
        logger.debug('Setting user language {}'.format(self))
        self.lang = lang

    def update_code(self, code):
        self.code = code

    def increase_mail_count(self):
        self.mail_count += 1

    def authorize(self):
        self.authorized = True

    def unauthorize(self):
        self.authorized = False

    def json(self):
        return json.dumps(self.__dict__)

    def __repr__(self):
        return 'USER: {ip} ({mac}) lang={lang} \
                authorized={authorized}'.format(**self.__dict__)


class Users(object):

    def __init__(self, urls_list, session_time):
        self.memcache = memcache.Client(urls_list)
        self.session_time = session_time

    def add(self, ip, mac, url='/index.html', lang='ru',
                  code='', mail_count=0, authorized=False):
        user = User(ip, mac, url, lang, code, mail_count, authorized)
        self.memcache.set(user.ip, user.json(), self.session_time)

    def get(self, ip):
        user_json = self.memcache.get(ip)
        user = None
        if user_json:
            user = User.from_json(user_json)
        return user

    def delete(self, user):
        self.memcache.delete(user.ip)
