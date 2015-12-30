from tornado.web import RequestHandler, MissingArgumentError


class AuthHandler(RequestHandler):
    def initialize(self):
        self.db = self.application.db
        self.auth = self.application.auth

    def get(self, *args, **kwargs):
        self.ip = self.request.remote_ip
        self.mac = self._get_mac()
        if not self.mac:
            self.redirect('/error.html')
        self.redirect('/index.html')

    def _get_mac(self):
        mac = None
        macs = self.get_arguments('mac')
        if macs:
            mac = macs[0]
        if not mac or mac == '00:00:00:00:00:00':
            with open('/proc/net/arp', 'r') as arp_file:
                for line in arp_file.readlines()[1:]:
                    (ip, _, _, mac_, _, _) = line.split()
                    if ip == self.ip:
                        mac = mac_
                        break
        return mac
