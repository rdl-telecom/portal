from tornado.web import RequestHandler, MissingArgumentError


class AuthHandler(RequestHandler):
    def initialize(self):
        self.db = self.application.db
        self.auth = self.application.auth
        self.radius_realm = self.application.radius_realm

    def get(self, *args, **kwargs):
        try:
            print self.ip
        except:
            print 'no ip'
        self.ip = self.request.remote_ip
        self.mac = self._get_mac()

        if not self.mac:                                   # No valid MAC address
            self.redirect('/error.html')

        self.code = self.db.get_user_code(self.mac)
        if not self.code:                                  # No such user in local DB
            self.redirect('/index.html')

        self.authenticated = self._authenticate()
        if not self.authenticated:                         # Hmmm... Strange error
            self.redirect('/error.html')

    def _authenticate(self):
        user_info = {
            'ip' : self.ip,
            'username' : self.mac.lower(),
            'realm' : self.radius_realm,
            'password' : self.code,
            'useragent' : self.request.headers.get('User-Agent', '<Unknown>'),
            'language' : self.request.headers.get('Accept-Language', 'ru')
        }
        future = self.auth.login(**user_info)
        if future.exception():
            return False
        else:
            return future.result()

    def _get_mac(self):
        mac = None
        macs = self.get_arguments('mac')
        if macs:
            mac = macs[0]
        if not mac or mac == '00:00:00:00:00:00':          # Invalid or missing MAC address in request
            with open('/proc/net/arp', 'r') as arp_file:
                for line in arp_file.readlines()[1:]:
                    (ip, _, _, mac_, _, _) = line.split()
                    if ip == self.ip:
                        mac = mac_
                        break
        return mac
