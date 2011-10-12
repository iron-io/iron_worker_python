# SimpleWorker For Python
import time
import json
import urllib2
import urllib
from poster.encode import multipart_encode
from poster.streaminghttp import register_openers


class SimpleWorker:
  def __init__(self, host, port, version, token):
    self.url = "http://"+host+":"+str(port) + "/"+str(version)+"/"
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

    url = self.url + 'projects/'+project_id+'?oauth=' + self.token
    return json.loads(self.__get(url))

  def getCodes(self, project_id = ''):
    if project_id == '':
      project_id = self.project_id
   
    url = self.url + 'projects/'+project_id+'/codes?oauth=' + self.token
    ret = json.loads(self.__get(url))
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
    data = json.dumps({"name":name,"standalone": True,"runtime":"python","file_name": runFilename,"version": self.version,"timestamp":ts,"oauth":self.token, "class_name" : name, "options" : {}, "access_key" : name})

    datagen, headers = multipart_encode({"file" : open(zipFilename, 'rb'), "data" : data})

    headers = dict(headers.items() + self.headers.items())
    req = urllib2.Request(url, datagen, headers)
    ret = urllib2.urlopen(req)
    return json.loads(ret.read())

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
     
    
  def postTask(self, project_id, name):
    if project_id == '':
      project_id = self.project_id
    url = self.url + 'projects/'+project_id+'/tasks?oauth=' + self.token
    print "postTask url:  " + url
    payload = [{"class_name" : name, "access_key" : name}]
    timestamp = time.asctime()
    data = {"payload" : payload, "class_name" : name, "name" : name, "options" : "{}", "token" : self.token, "api_version" : self.version , "version" : self.version, "timestamp" : timestamp, "oauth" : self.token, "access_key" : name}
    data = json.dumps(data)
    dataLen = len(data)
    headers = self.headers
    headers['Content-Type'] = "application/json"
    headers['Content-Length'] = str(dataLen)

    req = urllib2.Request(url, data, headers)
    ret = urllib2.urlopen(req)
    s = ret.read()
    msg = json.loads(s)
    task_id = msg['task_id']
    return task_id

  def getLog(self, project_id, task_id):
    url = self.url + 'projects/' + project_id + '/tasks/'+task_id+'/log/?oauth=' + self.token
    print "getLog url:  " + url
    del self.headers['Accept']
    del self.headers['Content-Type']
    del self.headers['Content-Length']
    body = self.__get(url)
    return body 
