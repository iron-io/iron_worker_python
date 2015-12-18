from __future__ import print_function

import os
import sys
if sys.version_info >= (3,):
    import http.client
else:
    import httplib
import mimetypes
import zipfile
import time
from dateutil.tz import *
import iron_core
try:
    import json
except ImportError:
    import simplejson as json


def file_exists(file):
    """Check if a file exists."""
    if not os.path.exists(file):
        return False
    try:
        open(file).close()
    except IOError:
        return False
    return True


class Task:
    id = None
    project = None
    code_id = None
    code_history_id = None
    schedule_id = None
    status = None
    code_name = None
    code_rev = None
    created_at = None
    updated_at = None
    start_time = None
    end_time = None
    duration = None
    timeout = 3600
    message = None
    delay = 0
    start_at = None
    end_at = None
    next_start = None
    last_run_time = None
    run_times = None
    run_count = None
    run_every = None
    percent = None
    payload = None
    priority = 0
    label = None
    cluster = None

    scheduled = False
    repeating = False

    __json_attrs = ["payload"]
    __rfc3339_attrs = ["created_at", "updated_at", "start_at", "end_at",
            "next_start", "last_run_time"]
    __timestamp_attrs = ["start_time", "end_time"]
    __schedule_attrs = ["start_at", "end_at", "next_start", "last_run_time",
            "run_count", "run_every"]
    __repeating_attrs = ["end_at", "next_start", "run_every"]
    __aliases = {
            "project": "project_id",
            "msg": "message"
    }
    __ignore = ["message"]

    def __str__(self):
        if self.id is not None and self.scheduled:
            return "IronWorker Scheduled Task #%s" % self.id
        elif self.id is not None:
            return "IronWorker Task #%s" % self.id
        else:
            return "IronWorker Task"

    def __repr__(self):
        return "<%s>" % str(self)

    def __set(self, attr, value):
        if attr in self.__rfc3339_attrs:
            if sys.version_info >= (3,):
                if isinstance(value, str):
                    value = iron_core.IronClient.fromRfc3339(value)
            else:
                if isinstance(value, basestring):
                    value = iron_core.IronClient.fromRfc3339(value)
        if attr in self.__schedule_attrs:
            self.scheduled = True
        if attr in self.__repeating_attrs:
            self.repeating = True
        if attr in self.__json_attrs:
            try:
                if sys.version_info >= (3,):
                    if isinstance(value, str):
                        value = json.loads(value)
                else:
                    if isinstance(value, basestring):
                        value = json.loads(value)
            except:
                pass
        setattr(self, attr, value)

    def __init__(self, values=None, **kwargs):
        if values is None:
            values = {}

        self.payload = {}

        attrs = [x for x in vars(self.__class__).keys()
                if not x.startswith("__")]

        for k in kwargs.keys():
            values[k] = kwargs[k]

        for prop in values.keys():
            if prop in attrs and prop not in self.__ignore:
                self.__set(prop, values[prop])
            elif prop in self.__aliases:
                self.__set(self.__aliases[prop], values[prop])


class CodePackage:
    id = None
    project = None
    name = None
    runtime = None
    latest_checksum = None
    revision = None
    latest_history_id = None
    latest_change = None
    files = None
    executable = None
    zip_path = None
    __rfc3339_attrs = ["latest_change"]
    __aliases = {
            "project_id": "project",
            "rev": "revision",
            "exec": "executable"
    }

    def __str__(self):
        if self.name is not None:
            return "%s Code Package" % self.name
        elif self.id is not None:
            return "Code Package #%s" % self.id
        else:
            return "IronWorker Code Package"

    def __repr__(self):
        return "<%s>" % str(self)

    def __set(self, attr, value):
        if attr in self.__rfc3339_attrs:
            value = iron_core.IronClient.fromRfc3339(value)
        setattr(self, attr, value)

    def __init__(self, values=None, **kwargs):
        if values is None:
            values = {}

        self.files = {}

        for k in kwargs.keys():
            values[k] = kwargs[k]

        attrs = [x for x in vars(self.__class__).keys()
                if not x.startswith("__")]

        for prop in values.keys():
            if prop in attrs:
                self.__set(prop, values[prop])
            elif prop in self.__aliases:
                self.__set(self.__aliases[prop], values[prop])

    def merge(self, target, ignoreRootDir=False):
        if os.path.isfile(target):
            self.files[os.path.basename(target)] = target
        elif os.path.isdir(target):
            for dirname, dirnames, filenames in os.walk(target):
                for filename in filenames:
                    path = os.path.join(dirname, filename)
                    if ignoreRootDir:
                        ziploc = path.lstrip(target).lstrip("/")
                    else:
                        ziploc = path
                    self.files[ziploc] = path
        else:
            raise ValueError("'%s' is not a file or directory." % target)
        if len(self.files) == 1:
            for dest, loc in self.files.items():
                self.executable = dest

    def merge_dependency(self, dep):
        dependency = __import__(dep)
        location = os.path.dirname(dependency.__file__)
        sys.stdout.write(str(location))

        parent = location.rstrip(os.path.basename(location))
        sys.stdout.write(str(parent))

        for dirname, dirnames, filenames in os.walk(location):
            for filename in filenames:
                path = os.path.join(dirname, filename)
            if path.startswith(parent):
                newpath = path[len(parent):]
            else:
                newpath = path
            ziploc = newpath.lstrip("/")
            self.files[ziploc] = path

    def zip(self, destination=None, overwrite=True):
        if destination is None:
            if self.name is not None:
                destination = "%s.zip" % self.name
            else:
                raise ValueError("Package name or destination is required.")
        if file_exists(destination) and not overwrite:
            raise ValueError("Destination '%s' already exists." % destination)
        filelist = self.files.copy()
        for dest, loc in filelist.items():
            if not file_exists(loc):
                del(self.files[dest])
        if len(self.files) > 0:
            z = zipfile.ZipFile(destination, "w")
            for dest, loc in self.files.items():
                z.write(loc, dest)
            z.close()
        self.zip_path = destination
        return file_exists(destination)


class IronWorker:
    NAME = "iron_worker_python"
    VERSION = "1.3.6"

    isLoaded = False
    arguments = {'task_id': None, 'dir': None, 'payload': None, 'config': None}

    def __init__(self, **kwargs):
        """Prepare a configured instance of the API wrapper and return it.

        Keyword arguments are passed directly to iron_core_python; consult its
        documentation for a full list and possible values."""
        self.client = iron_core.IronClient(name=IronWorker.NAME,
                version=IronWorker.VERSION, product="iron_worker", **kwargs)

    #############################################################
    ####################### CODE PACKAGES #######################
    #############################################################
    def codes(self):
        packages = []
        resp = self.client.get("codes")
        raw_packages = resp["body"]["codes"]
        for package in raw_packages:
            packages.append(CodePackage(package))
        return packages

    def code(self, id):
        if isinstance(id, CodePackage):
            id = id.id
        resp = self.client.get("codes/%s" % id)
        raw_package = resp["body"]
        return CodePackage(raw_package)

    def postCode(self, code, zipFilename=None):
        zip_loc = code.zip_path
        if zipFilename is not None:
            zip_loc = zipFilename
        if zip_loc is None:
            raise ValueError("Need to set the zip file to upload.")
        if not file_exists(zip_loc):
            raise ValueError("File doesn't exist: %s" % zip_loc)
        if code.name is None:
            raise ValueError("Code needs a name.")
        if code.executable is None:
            raise ValueError("Code's executable file needs to be set.")
        if code.runtime is None:
            code.runtime = "python"
        file = open(zip_loc, "rb")
        file_contents = file.read()
        file.close()

        data = [("data", json.dumps({
            "name": code.name,
            "runtime": code.runtime,
            "file_name": code.executable
        }))]

        files = [("file", zip_loc, file_contents)]

        content_type, body = IronWorker.encode_multipart_formdata(data, files)
        headers = {
                "Content-Type": content_type
        }
        resp = self.client.post(url="codes", body=body, headers=headers)
        return CodePackage(resp["body"])

    def upload(self, target, name=None, executable=None, overwrite=True):
        if isinstance(target, CodePackage):
            code = target
        else:
            code = CodePackage()
            code.merge(target)
        if name is not None:
            code.name = name
        if executable is not None:
            code.executable = executable
        if code.name is None:
            raise ValueError("Need to set a name for the package.")
        if code.executable is None:
            raise ValueError("Need to set a file as the executable.")
        clean_up = not file_exists("%s.zip" % code.name) or overwrite
        if code.zip_path is None or not file_exists(code.zip_path):
            code.zip(overwrite=overwrite)
        result = self.postCode(code)
        if clean_up:
            os.remove(code.zip_path)
        return result

    def deleteCode(self, id):
        if isinstance(id, CodePackage):
            id = id.id
        resp = self.client.delete("codes/%s" % id)
        return True

    def revisions(self, id):
        revisions = []
        if isinstance(id, CodePackage):
            id = id.id
        resp = self.client.get("codes/%s/revisions" % id)
        raw_revs = resp["body"]["revisions"]
        for rev in raw_revs:
            revisions.append(CodePackage(rev))
        return revisions

    def download(self, id, rev=None, destination=None):
        if isinstance(id, CodePackage):
            if rev is None and id.revision is not None:
                rev = id.revision
            id = id.id
        url = "codes/%s/download" % id
        if rev is not None:
            url = "%s?revision=%s" % (url, rev)
        resp = self.client.get(url)
        dest = resp["resp"].getheader("Content-Disposition")
        dest = dest.lstrip("filename=")
        if destination is not None:
            if os.path.isdir(destination):
                dest = os.path.join(destination, dest)
            else:
                dest = destination
        dup_dest = dest
        iteration = 1
        while file_exists(dup_dest) and destination is None:
            iteration += 1
            dup_dest = dest.rstrip(".zip") + " (" + str(iteration) + ").zip"
        f = open(dup_dest, "wb")
        f.write(resp["body"])
        f.close()
        return file_exists(dup_dest)

    #############################################################
    ########################## TASKS ############################
    #############################################################
    def tasks(self, scheduled=False, page=None, per_page=30):
        if not scheduled:
            resp = self.client.get("tasks")
            raw_tasks = resp["body"]
            raw_tasks = raw_tasks["tasks"]
        else:
            if per_page > 100:
                raise Exception("The limit for per_page is 100")
            query_params = "?per_page=" + str(per_page)
            if page is not None:
                query_params += "&page=" + page
            request_string = "schedules" + query_params
            resp = self.client.get(request_string)
            raw_tasks = resp["body"]
            raw_tasks = raw_tasks["schedules"]

        tasks = [Task(raw_task) for raw_task in raw_tasks]
        return tasks

    def tasks_by_code_name(self, code_name):
        tasks = []
        resp = self.client.get("tasks?code_name=%s" % code_name)
        raw_tasks = resp["body"]["tasks"]
        for raw_task in raw_tasks:
           tasks.append(Task(raw_task))
        return tasks

    def queue(self, task=None, tasks=None, retry=None, **kwargs):
        tasks_data = []
        if task is None:
            task = Task(**kwargs)
        if tasks is None:
            tasks = [task]
        for task in tasks:
            payload = task.payload
            if sys.version_info >= (3,):
                if not isinstance(payload, str):
                    payload = json.dumps(payload)
            else:
                if not isinstance(payload, basestring):
                    payload = json.dumps(payload)
            if task.code_name is None:
                raise ValueError("task.code_name is required.")
            task_data = {
                    "name": task.code_name,
                    "code_name": task.code_name,
                    "payload": payload,
                    "priority": task.priority,
                    "delay": task.delay,
                    "label": task.label,
                    "cluster": task.cluster
            }
            if not task.scheduled:
                type_str = "tasks"
                task_data["timeout"] = task.timeout
            else:
                type_str = "schedules"
                if task.run_every is not None:
                    task_data["run_every"] = task.run_every
                if task.end_at is not None:
                    if task.end_at.tzinfo is None:
                        task.end_at = task.end_at.replace(tzinfo=tzlocal())
                    task_data["end_at"] = iron_core.IronClient.toRfc3339(
                            task.end_at)
                if task.run_times is not None:
                    task_data["run_times"] = task.run_times
                if task.start_at is not None:
                    if task.start_at.tzinfo is None:
                        task.start_at = task.start_at.replace(tzinfo=tzlocal())
                    task_data["start_at"] = iron_core.IronClient.toRfc3339(
                            task.start_at)
                if task.timeout is not None:
                    task_data["timeout"] = task.timeout
                task_data["label"] = task.label
                task_data["cluster"] = task.cluster
            tasks_data.append(task_data)
        data = json.dumps({type_str: tasks_data})
        headers = {"Content-Type": "application/json"}

        if retry is not None:
            resp = self.client.post(type_str, body=data, headers=headers, retry=retry)
        else:
            resp = self.client.post(type_str, body=data, headers=headers)
        tasks = resp["body"]
        if len(tasks[type_str]) > 1:
            return [Task(task, scheduled=(type_str == "schedules"))
                    for task in tasks[type_str]]
        else:
            return Task(tasks[type_str][0],
                        scheduled=(type_str == "schedules"))

    def task(self, id, scheduled=False):
        if isinstance(id, Task):
            scheduled = id.scheduled
            id = id.id
        if not scheduled:
            url = "tasks/%s" % id
        else:
            url = "schedules/%s" % id
        resp = self.client.get(url)
        raw_task = resp["body"]
        return Task(raw_task)

    def log(self, id):
        if isinstance(id, Task):
            if id.scheduled:
                raise ValueError("Cannot retrieve a scheduled task's log.")
            id = id.id
        url = "tasks/%s/log" % id
        headers = {"Accept": "text/plain"}
        resp = self.client.get(url, headers=headers)
        return resp["body"]

    def setProgress(self, id, percent, msg=''):
        if isinstance(id, Task):
            id = id.id
        url = "tasks/%s/progress" % id
        body = {}
        body['percent'] = percent
        body['msg'] = msg
        body = json.dumps(body)
        resp = self.client.post(url, body=body,
                                headers={"Content-Type": "application/json"})
        return resp["body"]

    def retry(self, id, delay=1):
        if isinstance(id, Task):
            id = id.id
        url = "tasks/%s/retry" % id
        body = {}
        body['delay'] = delay
        body = json.dumps(body)
        resp = self.client.post(url, body=body,
                                headers={"Content-Type":"application/json"})
        return resp["body"]

    def cancel(self, id, scheduled=False):
        if isinstance(id, Task):
            scheduled = id.scheduled
            id = id.id
        if not scheduled:
            url = "tasks/%s/cancel" % id
        else:
            url = "schedules/%s/cancel" % id
        resp = self.client.post(url)
        return True

    #############################################################
    ######################### HELPERS ###########################
    #############################################################
    @staticmethod
    def encode_multipart_formdata(fields, files):
        """
        fields is a sequence of (name, value) elements for regular form fields.
        files is a sequence of (name, filename, value) elements for data to be
            uploaded as files
        Return (content_type, body) ready for httplib.HTTP instance
        """
        BOUNDARY = '----------ThIs_Is_tHe_bouNdaRY_$'
        CRLF = '\r\n'
        L = []
        for (key, value) in fields:
            L.append('--' + BOUNDARY)
            L.append('Content-Disposition: form-data; name="%s"' % key)
            L.append('')
            L.append(str(value))
        for (key, filename, value) in files:
            L.append('--' + BOUNDARY)
            L.append('Content-Disposition: form-data; name="%s"; filename="%s"'
                    % (key, filename))
            L.append('Content-Type: %s'
                    % IronWorker.get_content_type(filename))
            L.append('')
            L.append(str(value))
        L.append('--' + BOUNDARY + '--')
        L.append('')

        body = CRLF.join(L)
        content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
        return content_type, str(body)

    @staticmethod
    def get_content_type(filename):
        return mimetypes.guess_type(filename)[0] or 'application/octet-stream'

    @staticmethod
    def load_args():
        if IronWorker.isLoaded: return

        for i in range(len(sys.argv)):
            if sys.argv[i] == "-id":
                IronWorker.arguments['task_id'] = sys.argv[i + 1]
            if sys.argv[i] == "-d":
                IronWorker.arguments['dir'] = sys.argv[i + 1]
            if sys.argv[i] == "-payload":
                IronWorker.arguments['payload_file'] = sys.argv[i + 1]
            if sys.argv[i] == "-config":
                IronWorker.arguments['config_file'] = sys.argv[i + 1]

        if os.getenv('TASK_ID'): IronWorker.arguments['task_id'] = os.getenv('TASK_ID')
        if os.getenv('TASK_DIR'): IronWorker.arguments['dir'] = os.getenv('TASK_DIR')
        if os.getenv('PAYLOAD_FILE'): IronWorker.arguments['payload_file'] = os.getenv('PAYLOAD_FILE')
        if os.getenv('CONFIG_FILE'): IronWorker.arguments['config_file'] = os.getenv('CONFIG_FILE')

        if 'payload_file' in IronWorker.arguments and file_exists(IronWorker.arguments['payload_file']):
            f = open(IronWorker.arguments['payload_file'], "r")
            try:
                content = f.read()
                f.close()
                IronWorker.arguments['payload'] = json.loads(content)
            except Exception as e:
                print("Couldn't parse IronWorker payload into json, leaving as string. %s" % e)

        if 'config_file' in IronWorker.arguments and file_exists(IronWorker.arguments['config_file']):
            f = open(IronWorker.arguments['config_file'])
            try:
                content = f.read()
                f.close()
                IronWorker.arguments['config'] = json.loads(content)
            except Exception as e:
                print("Couldn't parse IronWorker config into json. %s" % e)

        IronWorker.isLoaded = True

    @staticmethod
    def payload():
        IronWorker.load_args()
        return IronWorker.arguments['payload']

    @staticmethod
    def config():
        IronWorker.load_args()
        return IronWorker.arguments['config']

    @staticmethod
    def task_id():
        IronWorker.load_args()
        return IronWorker.arguments['task_id']

    @staticmethod
    def task_dir():
        IronWorker.load_args()
        return IronWorker.arguments['dir']

    @staticmethod
    def args():
        IronWorker.load_args()
        return IronWorker.arguments

    @staticmethod
    def loaded():
        return IronWorker.isLoaded
