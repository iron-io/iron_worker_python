# IronWorker For Python
import time
from datetime import datetime
import json
import urllib2
import urllib
#from poster.encode import multipart_encode
#from poster.streaminghttp import register_openers
import hmac
#import sha
import base64
import hashlib

#class RequestWithMethod(urllib2.Request):
#    """Workaround for using DELETE with urllib2"""
#    def __init__(self, url, method, data=None, headers={},\
#        origin_req_host=None, unverifiable=False):
#        self._method = method
#        urllib2.Request.__init__(self, url, data, headers,\
#                 origin_req_host, unverifiable)
#
#    def get_method(self):
#        if self._method:
#            return self._method
#        else:
#            return urllib2.Request.get_method(self)
#

class CloudCache:
  def __init__(self, host, port=80, version, akey, skey, protocol="http", project_id=''):
    #self.url = "http://"+host+":"+str(port) + "/"+str(version)+"/"
    self.url = "%s://%s:%s/" % (protocol, host, port)
    #print "url = " + self.url
    self.host = host
    self.port = port
    self.akey = akey
    self.skey = skey
    self.version= version
    self.protocol = protocol
    self.project_id = ''
    self.headers = {}
    self.headers['Accept'] = "application/json"
    self.headers['Accept-Encoding'] = "gzip, deflate"
    self.headers['User-Agent'] = "CloudCache Python Pip v0.4"

  def __get(self, url, headers = {}):
    headers = dict(headers.items() + self.headers.items())
    #print "__get, url = " + url
    #print "__get , headers = " + str(headers)
    req = urllib2.Request(url, None, headers)
    ret = urllib2.urlopen(req)
    return ret.read()

  def __generate_timestamp(self, gmtime):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", gmtime)


  def __generate_signature(self, service, operation, timestamp, secret_access_key):
    #my_sha_hmac = hmac.new(secret_access_key, service + operation + timestamp, sha)
    my_sha_hmac = hmac.new(secret_access_key, service + operation + timestamp, hashlib.sha1)
    my_b64_hmac_digest = base64.encodestring(my_sha_hmac.hexdigest()).strip()
    #print "signature:  " + my_b64_hmac_digest
    return my_b64_hmac_digest


  def auth(self):
    ts = self.__generate_timestamp(time.gmtime())
    sig = self.__generate_signature(service="CloudCache", operation="auth", timestamp=ts, secret_access_key=self.skey)
  
    url = "%s://%s:%s/auth" % (self.protocol, self.hot, self.port)
    
    headers = {'User-Agent' : self.headers['User-Agent'], 'signature' : sig, 'timestamp' : ts, 'akey' : self.akey}

    req = urllib2.Request(url, None, headers)
    ret = urllib2.urlopen(req)
    return str(ret.read())

  def getmulti(self, keys):
    ts = self.__generate_timestamp(time.gmtime())
    sig = self.__generate_signature(service="CloudCache", operation="multi", timestamp=ts, secret_access_key=self.skey)
  
    url = "%s://%s:%s/getmulti" % (self.protocol, self.host, self.port)
    #print "getmulti url = " + url
    
    headers = {'User-Agent' : self.headers["User-Agent"], 'signature' : sig, 'timestamp' : ts, 'akey' : self.akey}
 
    #headers['HTTP_KEYS'] = json.dumps(keys)
    headers['keys'] = json.dumps(keys)

    #print "getmulti headers:  " + str(headers)
    req = urllib2.Request(url, None, headers)
    ret = urllib2.urlopen(req)
    return str(ret.read())
    
  def get(self, key):
    ts = self.__generate_timestamp(time.gmtime())
    sig = self.__generate_signature(service="CloudCache", operation="GET", timestamp=ts, secret_access_key=self.skey)
  
    url = "%s://%s:%s/%s" % (self.protocol, self.host, self.port, key)
    #print "get url = " + url
    
    headers = {'User-Agent' : self.headers['User-Agent'], 'signature' : sig, 'timestamp' : ts, 'akey' : self.akey}

    req = urllib2.Request(url, None, headers)
    ret = urllib2.urlopen(req)
    return str(ret.read())
    

  def set(self, key, val, ttl = 0):
    ts  = self.__generate_timestamp(time.gmtime())
    sig = self.__generate_signature(service="CloudCache", operation="POST", timestamp=ts, secret_access_key=self.skey)
  
    url = "%s://%s:%s/%s" % (self.protocol, self.host, self.port, key)

    #print "set (post) url = " + url
    headers = {'User-Agent' : self.headers['User-Agent'], 'signature' : sig, 'timestamp' : ts, 'akey' : self.akey}
    if ttl != 0:
      headers['ttl'] = ttl

    data = {"val" : val}
    data = urllib.urlencode(data)
    
    req = urllib2.Request(url, data, headers)
    ret = urllib2.urlopen(req)

    return str(ret.read())
