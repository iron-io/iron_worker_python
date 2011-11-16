# SimpleWorker For Python
import os
import sys
import time
from datetime import datetime
import json
import urllib2
import urllib
p1 = sys.path
p1 = p1[0]
sys.path.append(p1+'/poster-0.4')
print "path:  " + str(sys.path)
from poster.encode import multipart_encode
from poster.streaminghttp import register_openers
import ssl

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

class SimpleWorker:
  def __init__(self, host, port, version, token, protocol='http'):
    self.url = protocol +"://"+host+":"+str(port) + "/"+str(version)+"/"
    print "url = " + self.url
    self.token = token
    self.version= version
    self.project_id = ''
    self.headers = {}
    self.headers['Accept'] = "application/json"
    self.headers['Accept-Encoding'] = "gzip, deflate"
    self.headers['User-Agent'] = "SimpleWorker Python Pip v0.3"

  def __get(self, url, headers = {}):
    headers = dict(headers.items() + self.headers.items())
    print "__get, url = " + url
    print "__get , headers = " + str(headers)
    req = urllib2.Request(url, None, headers)
    ret = urllib2.urlopen(req)
    return ret.read() 

  def getTasks(self, project_id = ''):
    if project_id == '':
      project_id = self.project_id
    url = self.url + 'projects/'+project_id+'/tasks?oauth=' + self.token
    self.headers = {}
    self.headers['Accept'] = "application/json"
    self.headers['Accept-Encoding'] = "gzip, deflate"
    self.headers['User-Agent'] = "SimpleWorker Python Pip v0.3"
    body = self.__get(url)
    tasks = json.loads(body)
    return tasks['tasks']
    

  def getProjects(self):
    url = self.url + 'projects?oauth=' + self.token
    self.headers = {}
    self.headers['Accept'] = "application/json"
    self.headers['Accept-Encoding'] = "gzip, deflate"
    self.headers['User-Agent'] = "SimpleWorker Python Pip v0.3"
    body = self.__get(url)
    projects = json.loads(body)
    return projects['projects']

  def setProject(self, project_id):
    self.project_id = project_id

  def getProjectDetails(self, project_id = ''):
    if project_id == '':
      project_id = self.project_id

    self.headers = {}
    self.headers['Accept'] = "application/json"
    self.headers['Accept-Encoding'] = "gzip, deflate"
    self.headers['User-Agent'] = "SimpleWorker Python Pip v0.3"
    
    url = self.url + 'projects/'+project_id+'?oauth=' + self.token
    return json.loads(self.__get(url))

  def getCodes(self, project_id = ''):
    if project_id == '':
      project_id = self.project_id
   
    url = self.url + 'projects/'+project_id+'/codes?oauth=' + self.token
    body = self.__get(url)
    print "getCodes body = " + body
    ret = json.loads(body)
    return ret['codes']
     
  def getCodeDetails(self, code_id):
    project_id = self.project_id
    url = self.url + 'projects/'+project_id+'/codes/'+code_id+'?oauth=' + self.token
    print "getCodeDetails, url = " + url
    return json.loads(self.__get(url))
 
  def postCode(self, project_id, name, runFilename, zipFilename):
    if project_id == '':
      project_id = self.project_id
   
    url = self.url + 'projects/'+project_id+'/codes?oauth=' + self.token

    register_openers()
    ts = time.asctime()
    data = json.dumps({"code_name" : name, "name":name,"standalone": True,"runtime":"python","file_name": runFilename,"version": self.version,"timestamp":ts,"oauth":self.token, "class_name" : name, "options" : {}, "access_key" : name})

    datagen, headers = multipart_encode({"file" : open(zipFilename, 'rb'), "data" : data})

    headers = dict(headers.items() + self.headers.items())
    print "postCode, headers = " + str(headers)
    #print "postCode, datagen = " + str(datagen)
    print "postCode, data = " + str(data)
    req = urllib2.Request(url, datagen, headers)
    ret = urllib2.urlopen(req)
    body = ret.read()
    print "postCode returns this body:  " + body
    return json.loads(body)

  def postProject(self, name):
    url = self.url + 'projects?oauth=' + self.token
    payload = [{"name" : name, "class_name" : name, "access_key" : name}]
    timestamp = time.asctime()
    #data = {"payload" : payload, "oauth" : self.token, "version" : self.version, "timestamp" : timestamp, "options" : {}, "api_version" : self.version

    #data = {"payload" : payload}
    data = {"name" : name}
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
     
 
  def deleteProject(self, project_id):
    if project_id == '':
      project_id = self.project_id
    url = self.url + 'projects/'+project_id+'?oauth=' + self.token
    print "deleteProject url:  " + url
    req = RequestWithMethod(url, 'DELETE')
    ret = urllib2.urlopen(req)
    print "on deleteProject, urlopen returns:  " + str(ret)
    s = ret.read()
    print "body? " + str(s)
    #return json.loads(s)
    return
 
  def deleteCode(self, project_id, code_id):
    if project_id == '':
      project_id = self.project_id
    url = self.url + 'projects/'+project_id+'/codes/'+code_id+'?oauth=' + self.token
    print "deleteCode url:  " + url
    req = RequestWithMethod(url, 'DELETE')
    ret = urllib2.urlopen(req)
    print "on deleteCode, urlopen returns:  " + str(ret)
    s = ret.read()
    print "body? " + str(s)
    return

  def deleteTask(self, project_id, task_id):
    if project_id == '':
      project_id = self.project_id
    url = self.url + 'projects/'+project_id+'/tasks/'+task_id+'?oauth=' + self.token
    print "deleteTask url:  " + url
    req = RequestWithMethod(url, 'DELETE')
    ret = urllib2.urlopen(req)
    print "on deleteTask, urlopen returns:  " + str(ret)
    s = ret.read()
    print "body? " + str(s)
    #return json.loads(s)
    return

  def deleteSchedule(self, project_id, schedule_id):
    if project_id == '':
      project_id = self.project_id
    url = self.url + 'projects/'+project_id+'/schedules/'+schedule_id+'?oauth=' + self.token
    print "deleteSchedule url:  " + url
    req = RequestWithMethod(url, 'DELETE')
    ret = urllib2.urlopen(req)
    print "on deleteSchedule, urlopen returns:  " + str(ret)
    s = ret.read()
    print "body? " + str(s)
    #return json.loads(s)
    return
  
  def getSchedules(self, project_id):
    if project_id == '':
      project_id = self.project_id
    url = self.url + 'projects/'+project_id+'/schedules?oauth=' + self.token
    print "getSchedules url:  " + url
    self.headers = {}
    self.headers['Accept'] = "application/json"
    self.headers['Accept-Encoding'] = "gzip, deflate"
    self.headers['User-Agent'] = "SimpleWorker Python Pip v0.3"
    body = self.__get(url)
    schedules = json.loads(body)
    return schedules['schedules']
    
  def postSchedule(self, project_id, name, delay):
    # hash_to_send["payload"] = data
    # hash_to_send["class_name"] = class_name
    # hash_to_send["schedule"] = schedule - this is a hash too

    #delay = delay + int(time.time() + 0.5)
    #dt = datetime.fromtimestamp(delay + int(time.time()))
    #delay = dt.isoformat()
    #delay = time.asctime(time.gmtime(delay))
    #delay = (time.time() + delay) * 1.0e9
    #delay = (time.time() + delay)
    #delay = int(delay)
    print "delay = " + str(delay)
    #delay = time.gmtime(delay)

    if project_id == '':
      project_id = self.project_id
    url = self.url + 'projects/'+project_id+'/schedules?oauth=' + self.token
    print "postSchedule url:  " + url
    timestamp = time.asctime()
    
    #schedule = {"delay" : delay, "project_id" : project_id}
    schedule = {"delay" : delay, "code_name" : name}
    payload = {"schedule" : schedule, "project_id" : project_id, "class_name" : name, "name" : name, "options" : "{}", "token" : self.token, "api_version" : self.version , "version" : self.version, "timestamp" : timestamp, "oauth" : self.token, "access_key" : name, "delay" : delay}
    options = {"project_id" : project_id, "schedule" : schedule, "class_name" : name, "name" : name, "options" : "{}", "token" : self.token, "api_version" : self.version , "version" : self.version, "timestamp" : timestamp, "oauth" : self.token, "access_key" : name, "delay" : delay}
    data = {"project_id" : project_id, "schedule" : schedule, "class_name" : name, "name" : name, "options" : options, "token" : self.token, "api_version" : self.version , "version" : self.version, "timestamp" : timestamp, "oauth" : self.token, "access_key" : name, "delay" : delay , "payload" : payload}

    payload = [{"class_name" : name, "access_key" : name, "name" : name}]
    data =  {"name" : name, "delay" : delay, "payload" : payload}
    #data = json.dumps(data)
    schedules = [schedule]
    data = {"schedules" : schedules}
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
    # post schedules returns:  {"msg":"Scheduled","schedules":[{"id":"4ea35d11cddb1344fe00000c"}],"status_code":200}

    msg = json.loads(s)
    schedule_id = msg['schedules'][0]['id']
    return schedule_id

  def postTask(self, project_id, name):
    if project_id == '':
      project_id = self.project_id
    url = self.url + 'projects/'+project_id+'/tasks?oauth=' + self.token
    print "postTask url:  " + url
    payload = [{"class_name" : name, "access_key" : name, "code_name" : name}]
    timestamp = time.asctime()
    data = {"code_name" : name, "payload" : payload, "class_name" : name, "name" : name, "options" : "{}", "token" : self.token, "api_version" : self.version , "version" : self.version, "timestamp" : timestamp, "oauth" : self.token, "access_key" : name}
    #task = {"code_name" : name, "payload" : payload, "priority" : 0, "timeout" : 3600}
    payload = json.dumps(payload)
    task = {"name" : name, "code_name" : name, "payload" : payload}
    tasks = {"tasks" : [task]}
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
    # postTasks returns:  {"msg":"Queued up","status_code":200,"tasks":[{"id":"4ea35c4fcddb1344fe000007"}]}

    ret = json.loads(s)
    return ret

  def getLog(self, project_id, task_id):
    url = self.url + 'projects/' + project_id + '/tasks/'+task_id+'/log/?oauth=' + self.token
    print "getLog url:  " + url
    #del self.headers['Accept']
    self.headers['Accept'] = "text/plain"
    try:
      del self.headers['Content-Type']
      del self.headers['Content-Length']
    except:
      pass
    body = self.__get(url)
    return body 
