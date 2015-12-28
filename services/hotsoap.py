from xml.etree.ElementTree import Element, SubElement, tostring, fromstring

METHODS = {
    'Logon' : [ 'ip', 'realm', 'username', 'password', 'useragent', 'language' ],
    'Logoff' : [ 'ip' ],
    'GetStatus' : [ 'ip' ],
    'Allow' : [ 'ip', 'allowTime' ],
    'Deny' : [ 'ip' ]
}

RESPONSES = {
    'LogonResponse' : [ 'result' ],
    'LogoffResponse' : [ 'result' ],
    'StatusResult' : [ 'timestamp', 'rxOctets', 'txOctets', 'mac', 'ip', 'state' ],
    'AllowResponse' : [ 'result' ],
    'DenyResponse' : [ 'result' ]
}

ATTRIBS = {
    'xmlns:SOAP-ENV' : 'http://schemas.xmlsoap.org/soap/envelope/',
    'xmlns:SOAP-ENC' : 'http://schemas.xmlsoap.org/soap/encoding/',
    'xmlns:xsi' : 'http://www.w3.org/2001/XMLSchema-instance',
    'xmlns:xsd' : 'http://www.w3.org/2001/XMLSchema',
    'xmlns:hotspot' : 'http://ombord.info/hotspot.xsd'
}

class HotsoapRequest(object):
    def __init__(self, method, **kwargs):

        if method not in METHODS.keys():
            raise KeyError('No such method')

        base = self._make_base(method)
        for param in METHODS[method]:
            if param not in kwargs:
                raise KeyError("Required parameter '{}' is not specified".format(param))
            SubElement(base, param).text = kwargs[param] or "''"

        self._xml = '<?xml version="1.0" encoding="UTF-8"?>\n{}'.format(tostring(self._root, encoding="utf-8", method="xml"))

    def _make_base(self, method):
        self._root = Element('SOAP-ENV:Envelope', attrib=ATTRIBS)
        body = SubElement(self._root, 'SOAP-ENV:Body')
        return SubElement(body, 'hotspot:{}'.format(method))

    def __str__(self):
        return self._xml

    def __repr__(self):
        return self._xml

class HotsoapResponse(object):
    def __init__(self, xml):
        dom = fromstring(xml).find('{http://schemas.xmlsoap.org/soap/envelope/}Body')
        self._values = {}
        for resp in RESPONSES:
            result = dom.find('{{http://10.101.0.1/hotspot.xsd}}{}'.format(resp))
            if result is not None:
                self._type = resp
                for key in RESPONSES[resp]:
                    self._values[key] = result.find(key).text
                break

    def __str__(self):
        return self._values

    def __repr__(self):
        return '<{_type}> {_values}'.format(**self.__dict__)

    def __getitem__(self, key):
        return self._values[key]

