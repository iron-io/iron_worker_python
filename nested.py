from simple_worker_pip import *
import sys
import random
import string
import ConfigParser

config = ConfigParser.RawConfigParser()
config.read('config.ini')

token    = config.get("IronWorker", "token"  )
host     = config.get("IronWorker", "host"   )
port     = config.get("IronWorker", "port"   )
version  = config.get("IronWorker", "version")
protocol = config.get("IronWorker", "protocol")
project_id = config.get("IronWorker", "defaultProjectId")
sw = SimpleWorker(host, port, version, token, protocol)

name = "nested-" + str(time.time())
ret = sw.postCode(project_id, name, "nestedTask.py", "nested.zip")
print str(ret)

ret =  sw.postTask(project_id, name)
print "postTask returned:  " + str(ret)
task_id = ret['tasks'][0]['id']

