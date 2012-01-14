# IronWorker For Python
import os
import sys
import time
from datetime import datetime
import json
import urllib2
import urllib
from poster.encode import multipart_encode
from poster.streaminghttp import register_openers
import ssl
import zipfile


def file_exists(file):
    try:
        open(file)
    except IOError as e:
        return False
    else:
        return True


class RequestWithMethod(urllib2.Request):
    """Workaround for using DELETE with urllib2"""
    def __init__(self, url, method, data=None, headers={},\
        origin_req_host=None, unverifiable=False):
        self._method = method
        urllib2.Request.__init__(self, url, data, headers,\
                 origin_req_host, unverifiable)

    def get_method(self):
        if self._method:
            return self._method
        else:
            return urllib2.Request.get_method(self)


class IronWorker:
    DEFAULT_HOST = "worker-aws-us-east-1.iron.io"
    USER_AGENT = "IronWorker Python Pip v0.3"

    def __init__(self, token, project_id=None, host=DEFAULT_HOST, port=80,
            version=2, protocol='http'):
        self.url = "%s://%s:%s/%s/" % (protocol, host, port, version)
        print "url = " + self.url
        self.token = token
        self.version = version
        self.project_id = project_id
        self.headers = {}
        self.headers['Accept'] = "application/json"
        self.headers['Accept-Encoding'] = "gzip, deflate"
        self.headers['User-Agent'] = self.USER_AGENT

    def __get(self, url, headers={}):
        headers = dict(headers.items() + self.headers.items())
        print "__get, url = " + url
        print "__get , headers = " + str(headers)
        req = urllib2.Request(url, None, headers)
        ret = urllib2.urlopen(req)
        return ret.read()

    def getTasks(self, project_id=None):
        if project_id is None:
            project_id = self.project_id
        url = "%sprojects/%s/tasks?oauth=%s" % (self.url, project_id,
                self.token)
        self.headers = {}
        self.headers['Accept'] = "application/json"
        self.headers['Accept-Encoding'] = "gzip, deflate"
        self.headers['User-Agent'] = self.USER_AGENT
        body = self.__get(url)
        tasks = json.loads(body)
        return tasks['tasks']

    def getTaskDetails(self, task_id, project_id=""):
        if project_id == "":
            project_id = self.project_id
        url = "%sprojects/%s/tasks/%s?oauth=%s" % (self.url, project_id,
                task_id, self.token)
        self.headers = {}
        self.headers['Accept'] = "application/json"
        self.headers['Accept-Encoding'] = "gzip, deflate"
        self.headers['User-Agent'] = self.USER_AGENT
        body = self.__get(url)
        task = json.loads(body)
        return task

    def getProjects(self):
        url = self.url + 'projects?oauth=' + self.token
        self.headers = {}
        self.headers['Accept'] = "application/json"
        self.headers['Accept-Encoding'] = "gzip, deflate"
        self.headers['User-Agent'] = self.USER_AGENT
        body = self.__get(url)
        projects = json.loads(body)
        return projects['projects']

    def setProject(self, project_id):
        self.project_id = project_id

    def getProjectDetails(self, project_id=None):
        if project_id is None:
            project_id = self.project_id

        self.headers = {}
        self.headers['Accept'] = "application/json"
        self.headers['Accept-Encoding'] = "gzip, deflate"
        self.headers['User-Agent'] = self.USER_AGENT

        url = "%sprojects/%s?oauth=%s" % (self.url, project_id, self.token)
        return json.loads(self.__get(url))

    def getCodes(self, project_id=None):
        if project_id is None:
            project_id = self.project_id

        url = "%sprojects/%s/codes?oauth=%s" % (self.url, project_id,
                self.token)
        body = self.__get(url)
        print "getCodes body = " + body
        ret = json.loads(body)
        return ret['codes']

    def getCodeDetails(self, code_id):
        project_id = self.project_id
        url = "%sprojects/%s/codes/%s?oauth=%s" % (self.url, project_id,
                code_id, self.token)
        print "getCodeDetails, url = " + url
        return json.loads(self.__get(url))

    def postCode(self, name, runFilename, zipFilename, project_id=None):
        if project_id is None:
            project_id = self.project_id

        url = "%sprojects/%s/codes?oauth=%s" % (self.url, project_id,
                self.token)

        register_openers()
        ts = time.asctime()
        data = json.dumps({
            "code_name": name,
            "name": name,
            "standalone": True,
            "runtime": "python",
            "file_name": runFilename,
            "version": self.version,
            "timestamp": ts,
            "oauth": self.token,
            "class_name": name,
            "options": {},
            "access_key": name
        })

        datagen, headers = multipart_encode({
            "file": open(zipFilename, 'rb'),
            "data": data
        })

        headers = dict(headers.items() + self.headers.items())
        print "postCode, headers = " + str(headers)
        print "postCode, data = " + str(data)
        req = urllib2.Request(url, datagen, headers)
        ret = urllib2.urlopen(req)
        body = ret.read()
        print "postCode returns this body:  " + body
        return json.loads(body)

    def postProject(self, name):
        url = "%sprojects?oauth=%s" (self.url, self.token)
        payload = [{
            "name": name,
            "class_name": name,
            "access_key": name
        }]
        timestamp = time.asctime()

        data = {"name": name}
        data = json.dumps(data)
        dataLen = len(data)
        headers = self.headers
        headers['Content-Type'] = "application/json"
        headers['Content-Length'] = str(dataLen)

        req = urllib2.Request(url, data, headers)
        ret = urllib2.urlopen(req)
        s = ret.read()
        print "postProject returns:  " + s
        msg = json.loads(s)
        project_id = msg['id']
        return project_id

    def deleteProject(self, project_id=None):
        if project_id is None:
            project_id = self.project_id
        url = "%sprojects/%s?oauth%s" % (self.url, project_id, self.token)
        print "deleteProject url:  " + url
        req = RequestWithMethod(url, 'DELETE')
        ret = urllib2.urlopen(req)
        print "on deleteProject, urlopen returns:  " + str(ret)
        s = ret.read()
        print "body? " + str(s)
        return

    def deleteCode(self, code_id, project_id=None):
        if project_id is None:
            project_id = self.project_id
        url = "%sprojects/%s/codes/%s?oauth=%s" % (self.url, project_id,
                code_id, self.token)
        print "deleteCode url:  " + url
        req = RequestWithMethod(url, 'DELETE')
        ret = urllib2.urlopen(req)
        print "on deleteCode, urlopen returns:  " + str(ret)
        s = ret.read()
        print "body? " + str(s)
        return

    def deleteTask(self, task_id, project_id=None):
        if project_id is None:
            project_id = self.project_id
        url = "%sprojects/%s/tasks/%s?oauth=%s" % (self.url, project_id,
                task_id, self.token)
        print "deleteTask url:  " + url
        req = RequestWithMethod(url, 'DELETE')
        ret = urllib2.urlopen(req)
        print "on deleteTask, urlopen returns:  " + str(ret)
        s = ret.read()
        print "body? " + str(s)
        return

    def deleteSchedule(self, schedule_id, project_id=None):
        if project_id is None:
            project_id = self.project_id
        url = "%sprojects/%s/schedules/%s?oauth=%s" % (self.url, project_id,
                schedule_id, self.token)
        print "deleteSchedule url:  " + url
        req = RequestWithMethod(url, 'DELETE')
        ret = urllib2.urlopen(req)
        print "on deleteSchedule, urlopen returns:  " + str(ret)
        s = ret.read()
        print "body? " + str(s)
        return

    def getSchedules(self, project_id=None):
        if project_id is None:
            project_id = self.project_id
        url = "%sprojects/%s/schedules?oauth=%s" % (self.url, project_id,
                self.token)
        print "getSchedules url:  " + url
        self.headers = {}
        self.headers['Accept'] = "application/json"
        self.headers['Accept-Encoding'] = "gzip, deflate"
        self.headers['User-Agent'] = self.USER_AGENT
        body = self.__get(url)
        schedules = json.loads(body)
        return schedules['schedules']

    def postSchedule(self, name, delay, project_id=None):
        print "delay = " + str(delay)

        if project_id is None:
            project_id = self.project_id
        url = "%sprojects/%s/schedules?oauth=%s" % (self.url, project_id,
                self.token)
        print "postSchedule url:  " + url
        timestamp = time.asctime()

        schedules = [{"delay": delay, "code_name": name}]
        payload = [{
            "schedule": schedule,
            "project_id": project_id,
            "class_name": name,
            "name": name,
            "options": {},
            "token": self.token,
            "api_version": self.version,
            "version": self.version,
            "timestamp": timestamp,
            "oauth": self.token,
            "access_key": name,
            "delay": delay
        }]
        options = {
            "project_id": project_id,
            "schedule": schedule,
            "class_name": name,
            "name": name,
            "options": {},
            "token": self.token,
            "api_version": self.version,
            "version": self.version,
            "timestamp": timestamp,
            "oauth": self.token,
            "access_key": name,
            "delay": delay
        }

        data = {"schedules": schedules}
        data = json.dumps(data)
        print "data = " + data
        dataLen = len(data)
        headers = self.headers
        headers['Content-Type'] = "application/json"
        headers['Content-Length'] = str(dataLen)
        headers['Accept'] = "application/json"
        req = urllib2.Request(url, data, headers)
        ret = urllib2.urlopen(req)
        s = ret.read()
        print "post schedules returns:  " + s
        # post schedules returns
        # {"msg":"Scheduled","schedules":[{"id":"4ea35d11cddb1344fe00000c"}],
        #     "status_code":200}

        msg = json.loads(s)
        schedule_id = msg['schedules'][0]['id']
        return schedule_id

    def postTask(self, name, payload={}, project_id=None):
        if project_id is None:
            project_id = self.project_id
        url = "%sprojects/%s/tasks?oauth=%s" % (self.url, project_id,
                self.token)
        print "postTask url:  " + url
        #payload = [{
        #    "class_name": name,
        #    "access_key": name,
        #    "code_name": name
        #}]
        timestamp = time.asctime()
        data = {
            "code_name": name,
            "payload": payload,
            "class_name": name,
            "name": name,
            "options": {},
            "token": self.token,
            "api_version": self.version,
            "version": self.version,
            "timestamp": timestamp,
            "oauth": self.token,
            "access_key": name
        }
        payload = json.dumps(payload)
        task = {
            "name": name,
            "code_name": name,
            "payload": payload
        }
        tasks = {"tasks": [task]}
        data = json.dumps(tasks)
        print "postTasks, data = " + data
        dataLen = len(data)
        headers = self.headers
        headers['Content-Type'] = "application/json"
        headers['Content-Length'] = str(dataLen)

        req = urllib2.Request(url, data, headers)
        ret = urllib2.urlopen(req)
        s = ret.read()
        print "postTasks returns:  " + s
        # postTasks returns:
        # {"msg":"Queued up","status_code":200,
        #     "tasks":[{"id":"4ea35c4fcddb1344fe000007"}]}

        ret = json.loads(s)
        return ret

    def getLog(self, task_id, project_id=None):
        if project_id is None:
            project_id = self.project_id
        url = "%sprojects/%s/tasks/%s/log?oauth=%s" % (self.url, project_id,
                task_id, self.token)
        print "getLog url:  " + url
        self.headers['Accept'] = "text/plain"
        try:
            del self.headers['Content-Type']
            del self.headers['Content-Length']
        except:
            pass
        body = self.__get(url)
        return body

    @staticmethod
    def createZip(destination, base_dir='', files=[], overwrite=False):
        if file_exists(destination) and not overwrite:
            return False
        valid_files = []
        for file in files:
            if file_exists(file):
                valid_files.append(file)
        if len(valid_files) > 0:
            zip = zipfile.ZipFile(destination, "w")
            for file in valid_files:
                zip.write(file, os.path.join(base_dir, file))
            zip.close()
        return file_exists(destination)

    @staticmethod
    def zipDirectory(directory, destination, overwrite=False):
        if not os.path.isdir(directory):
            return False

        files = getFilenames(directory)
        if len(files) < 1:
            return False

        return createZip(files, destination, overwrite)

    @staticmethod
    def getFilenames(directory):
        names = []
        for dirname, dirnames, filenames in os.walk(directory):
            for filename in filenames:
                names.append(os.path.join(dirname, filename))
        return names
