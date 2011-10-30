from simple_worker_pip import *
import sys
import random
import string

token = "jTxYQDmMx5ZtVeZBT8jVx6oJDLw"
#token = "TSjcQAnNMZKWGdOyCJhxnN64CTk"
host= "174.129.54.171"
port = "8080"
version = "2"
#mq_project_id = "4e25e1d25c0dd27801000275"

sw = SimpleWorker(host, port, version, token)

projects = sw.getProjects()

print "getProjects returns:  " + str(projects)

for project in projects: 
  # Before deleting a project, delete all codes, tasks, schedules
  project_id = project['id']

  schedules = sw.getSchedules(project_id)
  for schedule in schedules:
    if schedule['status'] != 'cancelled':
      print "deleting schedule:  " + schedule['id']
      sw.deleteSchedule(project_id, schedule['id'])

  tasks = sw.getTasks(project_id)
  print "tasks = " + str(tasks)
  for task in tasks:
    if task['status'] != 'cancelled':
      print "deleting task:  " + task['id']
      sw.deleteTask(project_id, task['id'])  
  
  codes = sw.getCodes(project_id)
  for code in codes:
    print "deleting code:  " + code['id']
    sw.deleteCode(project_id, code['id'])  

  sw.deleteProject(project['id'])

projectName = "pip-gen-project-" + str(int(time.time()))
newProjectID = sw.postProject(projectName)

print "newProjectID = " + str(newProjectID)

project_id = newProjectID

print "project_id = " + project_id

sw.setProject(project_id)  # make this the default...

details = sw.getProjectDetails(project_id)

print "details:  " + str(details)

# Make a new code (drop): 

#name = "helloFromPython" + str(time.time())
#name = "helloFromPython-" + str(time.time())
s = ''.join(random.choice(string.ascii_uppercase) for x in range(10))
name = "HEREhelloFromPython" + s
print "creating code (drop) with name:  " + name
ret = sw.postCode(project_id, name, "hello.py", "hello.zip")
time.sleep(1)
print "postCode returned:  " + str(ret)

# For a given project_id, get list of Codes:

codes = sw.getCodes(project_id)

print "codes:  " + str(codes)
for code in codes:
  if code['name'] == name:
    print "newly created coder:  " + str(code)
    code_id = code['id']

code_id = codes[-1]['id']
print "code_id = " + code_id
#sys.exit()

# get details for specific code (drop)
details = sw.getCodeDetails(code_id)
print "code details:  " + str(details)


ret =  sw.postTask(project_id, name)
print "postTask returned:  " + str(ret)
task_id = ret['tasks'][0]['id']

print "About to sleep 30 to let task run..."
time.sleep(30)

logstr = sw.getLog(project_id, task_id)
print "sw.getLog returns:  " + str(logstr)

schedules = sw.getSchedules(project_id)
print "getSchedules returns:  " + str(schedules)


for schedule in schedules:
  if schedule['status'] != 'cancelled':
    print schedule['id']
    sw.deleteSchedule(project_id, schedule['id'])

schedule_id = sw.postSchedule(project_id, name, 10)
print "postSchedule returned:  " + str(schedule_id)

schedules = sw.getSchedules(project_id)
print "getSchedules returns:  " + str(schedules)
