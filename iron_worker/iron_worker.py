# IronWorker For Python
import os
import sys
import time
import urllib2
from poster.encode import multipart_encode
from poster.streaminghttp import register_openers
import zipfile
import ConfigParser
try:
    import json
except ImportError:
    import simplejson as json


def file_exists(file):
    """Check if a file exists."""
    try:
        open(file)
    except IOError:
        return False
    else:
        return True


class IllegalArgumentException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)


class RequestWithMethod(urllib2.Request):

    """Wrap urllib2 to make DELETE requests possible."""

    def __init__(self, url, method, data=None, headers={},
            origin_req_host=None, unverifiable=False):
        self._method = method
        return urllib2.Request.__init__(self, url, data, headers,
                origin_req_host, unverifiable)

    def get_method(self):
        if self._method:
            return self._method
        else:
            return urllib2.Request.get_method(self)


class IronWorker:
    DEFAULT_HOST = "worker-aws-us-east-1.iron.io"
    USER_AGENT = "IronWorker Python v0.3"

    def __init__(self, token=None, project_id=None, host=DEFAULT_HOST, port=80,
            version=2, protocol='http', config=None, app_engine=False):
        """Prepare a configured instance of the API wrapper and return it.

        Keyword arguments:
        token -- An API token found on http://hud.iron.io. Defaults to None.
        project_id -- The ID for the project, found on http://hud.iron.io
        host -- The hostname of the API server.
                Defaults to worker-aws-us-east-1.iron.io.
        port -- The port of the API server. Defaults to 80.
        version -- The API version to use. Defaults to 2.
        protocol -- The protocol to use. Defaults to http.
        config -- The config file to draw config values from. Defaults to None.
        app_engine -- Whether to run in App Engine compatibility mode.
                      Defaults to False.
        """
        self.token = token
        self.version = version
        self.project_id = project_id
        self.protocol = protocol
        self.host = host
        self.port = port
        self.version = version
        self.app_engine = app_engine
        if config is not None:
            config_file = ConfigParser.RawConfigParser()
            config_file.read(config)
            try:
                self.token = config_file.get("IronWorker", "token")
            except ConfigParser.NoOptionError:
                self.token = token
            try:
                self.project_id = config_file.get("IronWorker", "project_id")
            except ConfigParser.NoOptionError:
                self.project_id = project_id
            try:
                self.host = config_file.get("IronWorker", "host")
            except ConfigParser.NoOptionError:
                self.host = host
            try:
                self.port = config_file.get("IronWorker", "port")
            except ConfigParser.NoOptionError:
                self.port = port
            try:
                self.version = config_file.get("IronWorker", "version")
            except ConfigParser.NoOptionError:
                self.version = version
            try:
                self.protocol = config_file.get("IronWorker", "protocol")
            except ConfigParser.NoOptionError:
                self.protocol = protocol
        if self.token is None or self.project_id is None:
            raise IllegalArgumentException("Both token and project_id must \
                    have a value")
        self.url = "%s://%s:%s/%s/" % (self.protocol, self.host, self.port,
                self.version)
        self.__setCommonHeaders()

    def __get(self, url, headers={}):
        """Execute an HTTP GET request and return the result.

        Keyword arguments:
        url -- The url to execute the request against. (Required)
        headers -- A dict of headers to merge with self.headers and send
                   with the request.
        """
        headers = dict(headers.items() + self.headers.items())
        if not self.app_engine:
            req = urllib2.Request(url, None, headers)
            ret = urllib2.urlopen(req)
            return ret.read()
        else:
            from google.appengine.api import urlfetch
            return urlfetch.fetch(url=url, method=urlfetch.GET,
                    headers=headers).content

    def __post(self, url, payload={}, headers={}):
        """Execute an HTTP POST request and return the result.

        Keyword arguments:
        url -- The url to execute the request against. (Required)
        payload -- A dict of key-value form data to send with the
                   request. Will be urlencoded.
        headers -- A dict of headers to merge with self.headers and send
                   with the request.
        """
        headers = dict(headers.items() + self.headers.items())
        if not self.app_engine:
            req = urllib2.Request(url, payload, headers)
            ret = urllib2.urlopen(req)
            return ret.read()
        else:
            from google.appengine.api import urlfetch
            if not isinstance(payload, basestring):
                import urllib
                payload = urllib.urlencode(payload)
            return urlfetch.fetch(url=url, payload=payload,
                    method=urlfetch.POST, headers=headers).content

    def __delete(self, url, payload={}, headers={}):
        """Execute an HTTP DELETE request and return the result.

        Keyword arguments:
        url -- The url to execute the request against. (Required)
        payload -- A dict of key-value form data to send with the
                   request. Will be urlencoded.
        headers -- A dict of headers to merge with self.headers and send
                   with the request.
        """
        headers = dict(headers.items() + self.headers.items())
        if not self.app_engine:
            req = RequestWithMethod(url=url, method='DELETE', data=payload,
                    headers=headers)
            ret = urllib2.urlopen(req)
            s = ret.read()
        else:
            from google.appengine.api import urlfetch
            if not isinstance(payload, basestring):
                import urllib
                payload = urllib.urlencode(payload)
            return urlfetch.fetch(url=url, payload=payload,
                    method=urlfetch.DELETE, headers=headers).content

    def __setCommonHeaders(self):
        """Modify your headers to match the JSON default values."""
        self.headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip, deflate",
            "User-Agent": "IronWorker Python v0.3"
        }

    @staticmethod
    def getArgs():
        """Get the arguments that are passed to all IronWorkers as a dict"""
        args = {}
        for i in range(len(sys.argv)):
            if sys.argv[i].startswith("-") and (i + 1) < len(sys.argv):
                key = sys.argv[i][1:]
                i += 1
                args[key] = sys.argv[i]
        return args

    @staticmethod
    def getPayload():
        """Get the payload that was sent to a worker."""
        args = IronWorker.getArgs()
        if 'payload' in args and file_exists(args['payload']):
            return json.loads(open(args['payload']).read())

    @staticmethod
    def Rfc3339(timestamp=None):
        if timestamp is None:
            timestamp = time.gmtime()
        base = time.strftime("%Y-%m-%dT%H:%M:%S", timestamp)
        timezone = time.strftime("%z", timestamp)
        if timezone is not None and timezone != "+00:00":
            timezone = "%s:%s" % (timezone[:-2], timezone[-2:])
        elif timezone == "+00:00":
            timezone = "Z"
        return "%s%s" % (base, timezone)

    def getTasks(self, project_id=None):
        """Execute an HTTP request to get a list of tasks, and return it.

        Keyword arguments:
        project_id -- The project ID to get tasks from. Defaults to the
                      project ID set when initialising the wrapper.
        """
        self.__setCommonHeaders()
        if project_id is None:
            project_id = self.project_id
        url = "%sprojects/%s/tasks?oauth=%s" % (self.url, project_id,
                self.token)
        body = self.__get(url)
        tasks = json.loads(body)
        return tasks['tasks']

    def getTaskDetails(self, task_id, project_id=""):
        """Execute an HTTP request to get details on a specific task, and
        return it.

        Keyword arguments:
        task_id -- The ID of the task to get the details of. (Required)
        project_id -- The ID of the project the task belongs to. Defaults to
                      the project ID set when initialising the wrapper.
        """
        self.__setCommonHeaders()
        if project_id == "":
            project_id = self.project_id
        url = "%sprojects/%s/tasks/%s?oauth=%s" % (self.url, project_id,
                task_id, self.token)
        body = self.__get(url)
        task = json.loads(body)
        return task

    def getProjects(self):
        """Execute an HTTP request to get a list of projects and return it."""
        self.__setCommonHeaders()
        url = "%sprojects?oauth=%s" % (self.url, self.token)
        self.__setCommonHeaders()
        body = self.__get(url)
        projects = json.loads(body)
        return projects['projects']

    def setProject(self, project_id):
        """Set the default project ID for the wrapper.

        Keyword arguments:
        project_id -- The new project_id to use as the default. (Required)
        """
        self.project_id = project_id

    def getProjectDetails(self, project_id=None):
        """Execute an HTTP request to get the details of a project and return
        them.

        Keyword arguments:
        project_id -- The ID of the project to get details on. Defaults to the
                      project ID set when initialising the wrapper.
        """
        self.__setCommonHeaders()
        if project_id is None:
            project_id = self.project_id

        url = "%sprojects/%s?oauth=%s" % (self.url, project_id, self.token)
        return json.loads(self.__get(url))

    def getCodes(self, project_id=None):
        """Execute an HTTP request to get a list of code packages associated
        with a project, and return them.

        Keyword arguments:
        project_id -- The ID of the project whose code packages are to be
                      fetched. Defaults to the project ID set when initialising
                      the wrapper.
        """
        self.__setCommonHeaders()
        if project_id is None:
            project_id = self.project_id

        url = "%sprojects/%s/codes?oauth=%s" % (self.url, project_id,
                self.token)
        body = self.__get(url)
        ret = json.loads(body)
        return ret['codes']

    def getCodeDetails(self, code_id):
        """Execute an HTTP request to get the details of a specific code
        package.

        Keyword arguments:
        code_id -- The ID of the code package to fetch details on. (Required)
        """
        self.__setCommonHeaders()
        project_id = self.project_id
        url = "%sprojects/%s/codes/%s?oauth=%s" % (self.url, project_id,
                code_id, self.token)
        return json.loads(self.__get(url))

    def postCode(self, name, runFilename, zipFilename, project_id=None):

        """Upload a code package to the IronWorker servers, to be executed
        against later.

        Keyword arguments:
        name -- A label for the code package, used to refer to it. (Required)
        runFilename -- The filename to be executed when the code
                       is to be run. (Required)
        zipFilename -- The filename of a zip file containing the code
                       to be uploaded. (Required)
        project_id -- The project to upload the code package to. Defaults to
                      the project ID set when initialising the wrapper.
        """
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

        body = self.__post(url=url, payload=str().join(datagen),
                headers=headers)
        return json.loads(body)

    def postProject(self, name):
        """Create a new project on the IronWorker servers. Returns the new
        project's ID.

        Keyword arguments:
        name -- The name of the new project. (Required)
        """
        self.__setCommonHeaders()
        url = "%sprojects?oauth=%s" % (self.url, self.token)
        payload = [{
            "name": name,
            "class_name": name,
            "access_key": name
        }]

        data = {"name": name}
        data = json.dumps(data)
        dataLen = len(data)
        headers = self.headers
        headers['Content-Type'] = "application/json"
        headers['Content-Length'] = str(dataLen)

        s = self.__post(url=url, payload=data, headers=headers)
        msg = json.loads(s)
        project_id = msg['id']
        self.__setCommonHeaders()
        return project_id

    def deleteCode(self, code_id, project_id=None):
        """Execute an HTTP request to delete a code package.

        Keyword arguments:
        code_id -- The ID of the code package to be deleted. (Required)
        project_id -- The ID of the project that contains the code package.
                      Defaults to the project ID set when initialising the
                      wrapper.
        """
        self.__setCommonHeaders()
        if project_id is None:
            project_id = self.project_id
        url = "%sprojects/%s/codes/%s?oauth=%s" % (self.url, project_id,
                code_id, self.token)
        req = RequestWithMethod(url, 'DELETE')
        ret = urllib2.urlopen(req)
        s = ret.read()
        return

    def cancelTask(self, task_id, project_id=None):
        """Execute an HTTP request to cancel a task.

        Keyword arguments:
        task_id -- The ID of the task to be cancelled. (Required)
        project_id -- The ID of the project that contains the task. Defaults
                      to the project_id set when the wrapper was initialised.
        """
        self.__setCommonHeaders()
        if project_id is None:
            project_id = self.project_id
        url = "%sprojects/%s/tasks/%s/cancel?oauth=%s" % (self.url, project_id,
                task_id, self.token)
        data = json.dumps({})
        dataLen = len(data)
        headers = self.headers
        headers['Content-Type'] = "application/json"
        headers['Content-Length'] = str(dataLen)

        s = self.__post(url=url, payload=data, headers=headers)

        ret = json.loads(s)
        return ret

    def cancelSchedule(self, schedule_id, project_id=None):
        """Execute an HTTP request to cancel a task schedule.

        Keyword arguments:
        schedule_id -- The ID of the schedule to cancel. (Required)
        project_id -- The ID of the project that contains the schedule.
                      Defaults to the project_id set when the wrapper was
                      intialised.
        """
        self.__setCommonHeaders()
        if project_id is None:
            project_id = self.project_id
        url = "%sprojects/%s/schedules/%s/cancel?oauth=%s" % (self.url,
                project_id, schedule_id, self.token)
        data = json.dumps({})
        dataLen = len(data)
        headers = self.headers
        headers['Content-Type'] = "application/json"
        headers['Content-Length'] = str(dataLen)

        s = self.__post(url=url, payload=data, headers=headers)

        ret = json.loads(s)
        return ret

    def getSchedules(self, project_id=None):
        """Execute an HTTP request to get a list of task schedules and return
        them.

        Keyword arguments:
        project_id -- The ID of the project whose scheduled tasks are to be
                      retrieved. Defaults to the project ID set when the
                      wrapper was initialised.
        """
        self.__setCommonHeaders()
        if project_id is None:
            project_id = self.project_id
        url = "%sprojects/%s/schedules?oauth=%s" % (self.url, project_id,
                self.token)
        body = self.__get(url)
        schedules = json.loads(body)
        return schedules['schedules']

    def postSchedule(self, name, delay=None, payload={}, code_name=None,
            start_at=None, run_every=None, end_at=None, run_times=None,
            priority=0, project_id=None):

        """Execute an HTTP request to create a scheduled task that will be
        executed later.

        Keyword arguments:
        name -- A name for the schedule. (Required)
        delay -- The number of seconds to delay execution for.
                 Defaults to None.
        payload -- The payload of arguments to execute the task with. Defaults
                   to an empty dict.
        code_name -- The name of the code package to execute. Defaults to the
                     name of the schedule.
        start_at -- A Time or DateTime object indicating when the schedule
                    should start. Defaults to None.
        run_every -- The number of seconds between runs. If omitted, the
                     schedule will be run once. Defaults to None.
        end_at -- A Time or DateTime object indicating when the schedule should
                  end. Defaults to None.
        run_times -- The number of times to run the task. Defaults to None.
        priority -- The priority queue to run the job in (0, 1, 2). Run tasks
                    at higher priority to decrease the time they may spend on
                    queue once they come off the schedule. Defaults to 0.
        project_id -- The ID of the project to schedule the task under.
                      Defaults to the project ID set when the wrapper was
                      initialised.
        """

        self.__setCommonHeaders()
        if project_id is None:
            project_id = self.project_id
        if code_name is None:
            code_name = name
        url = "%sprojects/%s/schedules?oauth=%s" % (self.url, project_id,
                self.token)

        schedule = {
            "name": name
        }
        if delay is None and start_at is None:
            raise IllegalArgumentException("Either delay or start_at needs \
                    to be set.")
        if delay is not None and start_at is None:
            schedule['delay'] = delay
        elif delay is None and start_at is not None:
            schedule['start_at'] = IronWorker.Rfc3339(start_at)
        elif delay is not None and start_at is not None:
            schedule['start_at'] = IronWorker.Rfc3339(start_at)
        schedule['code_name'] = code_name
        if payload != {}:
            schedule['payload'] = json.dumps(payload)
        if run_every is not None:
            schedule['run_every'] = run_every
        if end_at is not None:
            schedule['end_at'] = IronWorker.Rfc3339(end_at)
        if run_times is not None:
            schedule['run_times'] = run_times
        schedule['priority'] = priority

        data = {"schedules": [schedule]}
        data = json.dumps(data)
        dataLen = len(data)
        headers = self.headers
        headers['Content-Type'] = "application/json"
        headers['Content-Length'] = str(dataLen)
        s = self.__post(url=url, payload=data, headers=headers)

        msg = json.loads(s)
        schedule_id = msg['schedules'][0]['id']
        self.__setCommonHeaders()
        return schedule_id

    def postTask(self, name, payload={}, project_id=None):
        """Executes an HTTP request to create a task that will be executed by
        the worker.

        Keyword arguments:
        name -- The name of the code package to execute against. (Required)
        payload -- Arguments to be passed to the task. Defaults to {}.
        project_id -- The ID of the project the task is to be created under.
                      Defaults to the project ID set when the wrapper was
                      initialised.
        """
        self.__setCommonHeaders()
        if project_id is None:
            project_id = self.project_id
        url = "%sprojects/%s/tasks?oauth=%s" % (self.url, project_id,
                self.token)
        payload = json.dumps(payload)
        task = {
            "name": name,
            "code_name": name,
            "payload": payload
        }
        tasks = {"tasks": [task]}
        data = json.dumps(tasks)
        dataLen = len(data)
        headers = self.headers
        headers['Content-Type'] = "application/json"
        headers['Content-Length'] = str(dataLen)

        s = self.__post(url=url, payload=data, headers=headers)

        ret = json.loads(s)
        return ret

    def getLog(self, task_id, project_id=None):
        """Executes an HTTP request to fetch the log associated with a task.

        Keyword arguments:
        task_id -- The ID of the task whose log is being retrieved.
        project_id -- The ID of the project that contains the task whose log is
                      being retrieved. Defaults to the project ID set when the
                      wrapper was initialised.
        """
        self.__setCommonHeaders()
        if project_id is None:
            project_id = self.project_id
        url = "%sprojects/%s/tasks/%s/log?oauth=%s" % (self.url, project_id,
                task_id, self.token)
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
        """Create a zip from an array of filenames.

        Keyword arguments:
        destination -- The filename or path the zip file is to be created
                       in. (Required)
        base_dir -- A directory tree within the zip file that all files will be
                    zipped under. Defaults to ''.
        files -- A list of files to included in the zip. Defaults to [].
        overwrite -- Whether the zip file should be overwritten if it exists.
                     Defaults to False.
        """
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
        """Create a zip from a directory. Passes through to createZip.

        Keyword arguments:
        directory -- The path to the directory to be zipped. (Required)
        destination -- The filename or path the zip file is to be created
                       in. (Required)
        overwrite -- Whether the zip file should be overwritten if it exists.
                     Defaults to False.
        """
        if not os.path.isdir(directory):
            return False

        files = IronWorker.getFilenames(directory)
        if len(files) < 1:
            return False

        return IronWorker.createZip(files, destination, overwrite)

    @staticmethod
    def getFilenames(directory):
        """Get a list of filenames and return it.

        Keyword arguments:
        directory -- The path to the directory whose filenames are to be
                     retrieved. (Required)
        """
        names = []
        for dirname, dirnames, filenames in os.walk(directory):
            for filename in filenames:
                names.append(os.path.join(dirname, filename))
        return names
