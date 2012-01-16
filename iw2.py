from iron_worker_pip import *
import sys
import random
import string
import ConfigParser
import ssl

config = ConfigParser.RawConfigParser()
config.read('config.ini')
token    = config.get("IronWorker", "token")
host     = config.get("IronWorker", "host" )
port     = config.get("IronWorker", "port" )
version  = config.get("IronWorker", "version")
protocol  = config.get("IronWorker", "protocol")
project_id = config.get("IronWorker", "project_id")

worker = IronWorker(host=host, port=port, version=version, token=token, protocol=protocol, project_id=project_id)

projects = worker.getProjects()

print "getProjects returns:  " + str(projects)

for project in projects: 
  # Before deleting a project, delete all codes, tasks, schedules
  project_id = project['id']

  schedules = worker.getSchedules()
  for schedule in schedules:
    if schedule['status'] != 'cancelled':
      print "deleting schedule:  " + schedule['id']
      worker.deleteSchedule(schedule_id=schedule['id'])

  #tasks = worker.getTasks(project_id=project_id)
  tasks = []
  print "tasks = " + str(tasks)
  for task in tasks:
    if task['status'] != 'cancelled':
      print "deleting task:  " + task['id']
      worker.deleteTask(task_id=task['id'])  
  
  codes = worker.getCodes()
  # delete the first one, do another getCodes, make sure it's not there
  try:
    code_id = codes[0]['id']
  except:
    continue
  #worker.deleteCode(code_idcode_id)
  codes = worker.getCodes()
  for code in codes:
    if (code_id == code['id']):
      print "Woop! I thought I deleted this code!  " + code_id
    print "deleting code:  " + code['id']
    #worker.deleteCode(code_id=code['id'])  

  #worker.deleteProject()

projectName = "pip-gen-project-" + str(int(time.time()))
newProjectID = worker.postProject(name=projectName)

print "newProjectID = " + str(newProjectID)

project_id = newProjectID

print "project_id = " + project_id

worker.setProject(project_id=project_id)  # make this the default...

details = worker.getProjectDetails()

print "details:  " + str(details)

# Make a new code (drop): 

#name = "helloFromPython" + str(time.time())
#name = "helloFromPython-" + str(time.time())
s = ''.join(random.choice(string.ascii_uppercase) for x in range(10))
name = "helloFromPython" + s
print "creating code (drop) with name:  " + name
ret = worker.postCode(name=name, runFilename="hello.py", zipFilename="hello.zip")
time.sleep(1)
print "postCode returned:  " + str(ret)
#sys.exit()
# For a given project_id, get list of Codes:

codes = worker.getCodes()

print "codes:  " + str(codes)
for code in codes:
  if code['name'] == name:
    print "newly created coder:  " + str(code)
    code_id = code['id']

code_id = codes[1]['id']
print "code_id = " + code_id
#sys.exit()

# get details for specific code (drop)
details = worker.getCodeDetails(code_id)
print "code details:  " + str(details)


ret =  worker.postTask(name=name)
print "postTask returned:  " + str(ret)
task_id = ret['tasks'][0]['id']

try: 
  logstr = worker.getLog(task_id=task_id)
except urllib2.HTTPError, e:
  if e.code == 404:
    print "Got expected 404 when attempting to get log right away..."
  else:
    print "Unexpected HTTP error:  " + str(e)
    sys.exit()

print "About to sleep 30 to let task run..."
time.sleep(30)

logstr = worker.getLog(task_id=task_id)
print "worker.getLog returns:  " + str(logstr)
sys.exit()
schedules = worker.getSchedules()
print "getSchedules returns:  " + str(schedules)


for schedule in schedules:
  if schedule['status'] != 'cancelled':
    print schedule['id']
    worker.deleteSchedule(schedule_id=schedule['id'])

schedule_id = worker.postSchedule(name=name, delay=10)
print "postSchedule returned:  " + str(schedule_id)

schedules = worker.getSchedules()
print "getSchedules returns:  " + str(schedules)
