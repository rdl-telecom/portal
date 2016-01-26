import logging
import re


class Checker(object):

    def __init__(self):
        self.re_code = re.compile(r'[0-9ABCDEFGHJKLMNPQRSTVWXZ]{7}')
        self.re_email = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-.]+\.[a-z]{2,6}$')
        self.re_phone = re.compile(r'^[0-9]{10,16}$')

    def is_code(self, text):
    	return self.re_code.match(text) is not None

    def is_email(self, text):
        return self.re_email.match(text) is not None

    def is_phone(self, text):
    	return self.re_phone.match(text) is not None