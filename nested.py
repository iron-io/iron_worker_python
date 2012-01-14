from iron_worker_pip import *
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
project_id = config.get("IronWorker", "project_id")
worker = IronWorker(host=host, port=port, version=version, token=token, protocol=protocol, project_id=project_id)

name = "nested-" + str(time.time())
ret = worker.postCode(name=name, runFilename="nestedTask.py", zipFilename="nested.zip")
print str(ret)

ret =  worker.postTask(name=name)
print "postTask returned:  " + str(ret)
task_id = ret['tasks'][0]['id']

