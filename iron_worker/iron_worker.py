# IronWorker For Python
import os
import sys
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


class IronWorker:
        AWS_HOST = "worker-aws-us-east-1.iron.io"
        NAME = "iron_worker_python"
        VERSION = "0.1.0"
        API_VERSION = 2

        def __init__(self, token=None, project_id=None, host=AWS_HOST,
                        port=443, version=API_VERSION, protocol='https',
                        config=None):
                """Prepare a configured instance of the API wrapper and
                return it.

                Keyword arguments:
                token -- An API token found on http://hud.iron.io. Defaults
                         to None.
                project_id -- The ID for the project, found on
                              http://hud.iron.io
                host -- The hostname of the API server. Defaults to AWS_HOST.
                port -- The port of the API server. Defaults to 443.
                version -- The API version to use. Defaults to API_VERSION.
                protocol -- The protocol to use. Defaults to https.
                config -- The config file to draw config values from. Defaults
                          to None.
                """
                self.token = token
                self.version = version
                self.project_id = project_id
                self.protocol = protocol
                self.host = host
                self.port = port
                self.version = version
                if config is not None:
                        config_file = ConfigParser.RawConfigParser()
                        config_file.read(config)
                try:
                        self.token = config_file.get("IronWorker", "token")
                except ConfigParser.NoOptionError:
                        self.token = token
                try:
                        self.project_id = config_file.get("IronWorker",
                                        "project_id")
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
                        self.protocol = config_file.get("IronWorker",
                                        "protocol")
                except ConfigParser.NoOptionError:
                        self.protocol = protocol
                if self.token is None or self.project_id is None:
                        raise ValueError("Both token and project_id \
                                        must have a value")
                        self.client = iron_rest.IronClient(name=NAME,
                                        version=VERSION, host=self.host,
                                        project_id=self.project_id,
                                        token=self.project_id,
                                        protocol=self.protocol, port=self.port,
                                        api_version=API_VERSION)

        @staticmethod
        def getArgs():
                """Get the arguments that are passed to all IronWorkers
                as a dict"""
                args = {}
                num_args = len(sys.argv) - 1
                for i in range(len(sys.argv)):
                        if sys.argv[i].startswith("-") and i < num_args:
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

        def getTasks(self):
                """Execute an HTTP request to get a list of tasks, and
                return it.
                """
                resp = self.client.get("tasks")
                tasks = json.loads(body["body"])
                return tasks['tasks']

        def getTaskDetails(self, task_id):
                """Execute an HTTP request to get details on a specific task,
                and return it.

                Keyword arguments:
                task_id -- The ID of the task to get the details of. Required.
                """
                url = "tasks/%s" % task_id
                body = self.client.get(url)
                task = json.loads(body["body"])
                return task

        def getProjectDetails(self):
                """Execute an HTTP request to get the details of a project and
                return them.
                """
                return json.loads(self.client.get("")["body"])

        def getCodes(self):
                """Execute an HTTP request to get a list of code packages
                associated with a project, and return them.
                """
                resp = self.client.get("codes")
                ret = json.loads(resp['body'])
                return ret['codes']

        def getCodeDetails(self, code_id):
                """Execute an HTTP request to get the details of a specific
                code package.

                Keyword arguments:
                code_id -- The ID of the code package to fetch details on.
                           Required.
                """
                url = "codes/%s" % code_id
                resp = self.client.get(url)
                return json.loads(resp["body"])

        def postCode(self, name, runFilename, zipFilename):
                """Upload a code package to the IronWorker servers, to be
                executed against later.

                Keyword arguments:
                name -- A label for the code package, used to refer to it.
                        Required.
                runFilename -- The filename to be executed when the code
                               is to be run. Required.
                zipFilename -- The filename of a zip file containing the code
                               to be uploaded. Required.
                """

                register_openers()
                data = json.dumps({
                        "name": name,
                        "runtime": "python",
                        "file_name": runFilename
                })

                datagen, headers = multipart_encode({
                        "file": open(zipFilename, 'rb'),
                        "data": data
                })

                resp = self.client.post(url=url, body=str().join(datagen),
                                headers=headers)
                return json.loads(resp['body'])

        def deleteCode(self, code_id):
                """Execute an HTTP request to delete a code package.

                Keyword arguments:
                code_id -- The ID of the code package to be deleted. Required.
                """
                url = "codes/%s" % code_id
                resp = self.client.delete(url)
                return json.loads(resp["body"])

        def cancelTask(self, task_id):
                """Execute an HTTP request to cancel a task.

                Keyword arguments:
                task_id -- The ID of the task to be cancelled. Required.
                """
                url = "tasks/%s/cancel" % task_id
                resp = self.client.post(url)
                return json.loads(resp["body"])

        def cancelSchedule(self, schedule_id):
                """Execute an HTTP request to cancel a task schedule.

                Keyword arguments:
                schedule_id -- The ID of the schedule to cancel. Required.
                """
                url = "schedules/%s/cancel" % schedule_id
                resp = self.client.post(url=url)
                return json.loads(resp["body"])

        def getSchedules(self):
                """Execute an HTTP request to get a list of task schedules and
                return them.
                """
                resp = self.client.get("schedules")
                schedules = json.loads(resp["body"])
                return schedules['schedules']

        def postSchedule(self, name, delay=None, payload={}, code_name=None,
                start_at=None, run_every=None, end_at=None, run_times=None,
                priority=0):

                """Execute an HTTP request to create a scheduled task that
                will be executed later or repeatedly.

                Keyword arguments:
                name -- A name for the schedule. Required.
                delay -- The number of seconds to delay execution for.
                         Defaults to None.
                payload -- The payload of arguments to execute the task with.
                           Defaults to an empty dict.
                code_name -- The name of the code package to execute. Defaults
                             to the name of the schedule.
                start_at -- A Time or DateTime object indicating when the
                            schedule should start. Defaults to None.
                run_every -- The number of seconds between runs. If omitted,
                             the schedule will be run once. Defaults to None.
                end_at -- A Time or DateTime object indicating when the
                          schedule should end. Defaults to None.
                run_times -- The number of times to run the task. Defaults to
                             None.
                priority -- The priority queue to run the job in (0, 1, 2).
                            Run tasks at a higher priority to decrease the time
                            they may spend on queue once they come off the
                            schedule. Defaults to 0.
                """
                if code_name is None:
                        code_name = name
                schedule = {
                        "name": name
                }
                if delay is None and start_at is None:
                        raise ValueError("Either delay or start_at needs \
                                to be set.")
                if delay is not None and start_at is None:
                        schedule['delay'] = delay
                elif delay is None and start_at is not None:
                        schedule['start_at'] = IronWorker.Rfc3339(start_at)
                elif delay is not None and start_at is not None:
                        schedule['start_at'] = IronWorker.Rfc3339(start_at)
                schedule['code_name'] = code_name
                schedule['payload'] = json.dumps(payload)
                if run_every is not None:
                        schedule['run_every'] = run_every
                if end_at is not None:
                        schedule['end_at'] = IronWorker.Rfc3339(end_at)
                if run_times is not None:
                        schedule['run_times'] = run_times
                schedule['priority'] = priority

                data = json.dumps({"schedules": [schedule]})
                headers = {"Content-Type": "application/json"}
                resp = self.client.post("schedules", body=data,
                                headers=headers)
                body = json.loads(resp["body"])
                return body["schedules"]

        def postTask(self, name, payload={}):
                """Executes an HTTP request to create a task that will be
                executed by the worker.

                Keyword arguments:
                name -- The name of the code package to execute against.
                        Required.
                payload -- Arguments to be passed to the task. Defaults to {}.
                """
                payload = json.dumps(payload)
                task = {
                        "name": name,
                        "code_name": name,
                        "payload": payload
                }
                tasks = {"tasks": [task]}
                data = json.dumps(tasks)
                headers = {"Content-Type": "application/json"}

                resp = self.client.post("tasks", body=data, headers=headers)

                return json.loads(resp["body"])

        def getLog(self, task_id):
                """Executes an HTTP request to fetch the log associated with a
                task.

                Keyword arguments:
                task_id -- The ID of the task whose log is being retrieved.
                """
                url = "tasks/%s/log" % task_id
                headers = {'Accept': "text/plain"}
                resp = self.client.get(url, headers=headers)
                return json.loads(resp["body"])

        @staticmethod
        def createZip(destination, base_dir='', files=[], overwrite=False):
                """Create a zip from an array of filenames.

                Keyword arguments:
                destination -- The filename or path the zip file is to be
                               created in. Required.
                base_dir -- A directory tree within the zip file that all files
                            will be zipped under. Defaults to ''.
                files -- A list of files to included in the zip. Defaults
                         to [].
                overwrite -- Whether the zip file should be overwritten if it
                             exists. Defaults to False.
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
                directory -- The path to the directory to be zipped. Required.
                destination -- The filename or path the zip file is to be
                               created in. Required.
                overwrite -- Whether the zip file should be overwritten if it
                             exists. Defaults to False.
                """
                if not os.path.isdir(directory):
                        return False

                files = IronWorker.getFilenames(directory)
                if len(files) < 1:
                        return False

                return IronWorker.createZip(files=files, overwrite=overwrite,
                                destination=destination)

        @staticmethod
        def getFilenames(directory):
                """Get a list of filenames and return it.

                Keyword arguments:
                directory -- The path to the directory whose filenames are to
                             be retrieved. Required.
                """
                names = []
                for dirname, dirnames, filenames in os.walk(directory):
                        for filename in filenames:
                                names.append(os.path.join(dirname, filename))
                return names
