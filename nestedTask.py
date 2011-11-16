import json
import urllib2
import hashlib
import cloudcache 
import ConfigParser
import os
import sys
from simple_worker_pip import *

try:
  dr = sys.argv[2]
  print "directory:  " + dr
except:
  dr = './'
config = ConfigParser.RawConfigParser()
pth = os.path.abspath(dr + 'config.ini')
fp = open(pth, 'r')
config.readfp(fp)

token    = config.get("IronWorker", "token"  )
host     = config.get("IronWorker", "host"   )
port     = config.get("IronWorker", "port"   )
version  = config.get("IronWorker", "version")
protocol = config.get("IronWorker", "protocol")
project_id = config.get("IronWorker", "defaultProjectId")
sw = SimpleWorker(host, port, version, token, protocol)

name = "NestedTask-B-" + str(time.time())

zfn = dr + "hello.zip"
ret = sw.postCode(project_id, name, "hello.py", zfn)

ret =  sw.postTask(project_id, name)
print "postTask returned:  " + str(ret)
task_id = ret['tasks'][0]['id']

print "Nested task creation returns:  " + str(task_id)



