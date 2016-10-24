import httplib
import time

import requests

httplib.HTTPConnection._http_vsn = 10
httplib.HTTPConnection._http_vsn_str = 'HTTP/1.1'

s = requests.Session()

for i in xrange(0, 10):
    r = s.get('http://127.0.0.1:8080/', headers={'Connection': 'keep-alive'})
    r = s.get('http://127.0.0.1:8080/test.html', headers={'Connection': 'keep-alive'})
    print r.headers

time.sleep(14)

"""
httplib.HTTPConnection._http_vsn = 10
httplib.HTTPConnection._http_vsn_str = 'HTTP/1.0'

for i in xrange(0,10):
    r = requests.get('http://127.0.0.1:8081/',headers={'Connection': 'keep-alive'})
    r = requests.get('http://127.0.0.1:8081/test.html',headers={'Connection': 'keep-alive'})
    print r.headers

time.sleep(10)
"""
