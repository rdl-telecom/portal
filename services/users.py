import logging
import json

import memcache

logger = logging.getLogger(__name__)


class User(object):

    def __init__(self, ip, mac, phone='', url='/index.html', lang='ru',
                       code='', mail_count=0, authorized=False, step='phone'):
        logger.debug('Creating user object IP={} MAC={}'.format(ip, mac))
        self.ip = ip
        self.mac = mac.lower()
        self.phone = phone
        self.url = url
        self.lang = lang
        self.code = code.upper()
        self.mail_count = mail_count
        self.authorized = authorized
        self.step = step

    @staticmethod
    def from_json(user_json):
        user_dict = json.loads(user_json)
        return User(**user_dict)

    def update_lang(self, lang):
        logger.debug('Setting user language: {}'.format(self))
        self.lang = lang

    def update_code(self, code):
        logger.debug('Updating user code: {}'.format(self))
        self.code = code

    def update_phone(self, phone):
        logger.debug('Updating user phone: {}'.format(self))
        self.phone = phone

    def increase_mail_count(self):
        logger.debug('Increasing mail_count: {}'.format(self))
        self.mail_count += 1

    def authorize(self):
        logger.debug('Authorizing: {}'.format(self))
        self.authorized = True

    def unauthorize(self):
        logger.debug('Unauthorizing: {}'.format(self))
        self.authorized = False

    def next_step(self, step):
        self.step = step

    def json(self):
        return json.dumps(self.__dict__)

    def __repr__(self):
        return ' '.join(('USER: {ip} ({mac}) lang={lang}',
                         'authorized={authorized} code={code}',
                         'phone={phone} mail_count={mail_count}'))\
                         .format(**self.__dict__)


class Users(object):

    def __init__(self, urls_list, session_time):
        self.memcache = memcache.Client(urls_list)
        self.session_time = session_time

    def add(self, ip, mac, phone='', url='/index.html', lang='ru',
                  code='', mail_count=0, authorized=False, step='phone'):
        user = User(ip, mac, phone, url, lang, code, mail_count, authorized)
        self.memcache.set(user.ip, user.json(), self.session_time)
        return user

    def get(self, ip):
        user_json = self.memcache.get(ip)
        user = None
        if user_json:
            user = User.from_json(user_json)
        return user

    def update(self, user):
        self.memcache.set(user.ip, user.json(), self.session_time)

    def delete(self, user):
        self.memcache.delete(user.ip)
