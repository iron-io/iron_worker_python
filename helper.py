import urllib2
import urllib
import sys
try:
        import json
except ImportError:
        import simplejson as json

DEFAULT_HOST = "worker-aws-us-east-1.iron.io"
USER_AGENT = "IronWorker Python v0.3"


def getArgs():
        """Get the arguments that are passed to all IronWorkers as a dict"""
        args = {}
        for i in range(len(sys.argv)):
                if sys.argv[i].startswith("-") and (i + 1) < len(sys.argv):
                        key = sys.argv[i][1:]
                        i += 1
                        args[key] = sys.argv[i]
        return args


def getArg(key):
        args = getArgs()
        return args[key]


def setTaskProgress(token, percent=None, message=None, project_id=None,
                task_id=None, host=DEFAULT_HOST, port=80, version=2,
                protocol="http"):
        if percent is None and message is None:
                return
        payload = {}
        if percent is not None:
                payload["percent"] = percent
        if message is not None:
                payload["msg"] = message
        if task_id is None:
                task_id = getArg("id")
        url = "%s://%s:%s/%s/projects/%s/tasks/%s/progress?oauth=%s" % (
                        protocol, host, port, version, project_id, task_id,
                        token)
        headers = {
                        "Accept": "application/json",
                        "Accept-Encoding": "gzip, deflate",
                        "User-Agent": USER_AGENT
        }
        data = json.dumps(payload)
        dataLen = len(data)
        headers['Content-Type'] = "application/json"
        headers['Content-Length'] = str(dataLen)
        req = urllib2.Request(url, data, headers)
        ret = urllib2.urlopen(req)
        return ret.read()
