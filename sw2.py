from simple_worker_pip import *
import sys

token = "your token here"
host= "your host here"
port = "8080"
version = "2"

sw = SimpleWorker(host, port, version, token)

projectName = "pip-gen-" + str(int(time.time()))
newProject = sw.postProject(projectName)

projects = sw.getProjects()

print str(projects)

project_id = projects[0]['id']

print "project_id = " + project_id

sw.setProject(project_id)  # make this the default...

details = sw.getProjectDetails(project_id)

print "details:  " + str(details)

# Make a new worker:

name = "helloFromPython-" + str(time.time())
print "creating worker with name:  " + name
ret = sw.postWorker(project_id, name, "hello.py", "hello.zip")
time.sleep(1)
print "postWorker returned:  " + str(ret)

# For a given project_id, get list of workers:

workers = sw.getWorkers(project_id)

#print "workers:  " + str(workers)
for worker in workers:
  if worker['name'] == name:
    print "newly created worker:  " + str(worker)
    worker_id = worker['id']

worker_id = workers[-1]['id']
print "worker_id = " + worker_id
#sys.exit()

# get details for specific worker
details = sw.getWorkerDetails(worker_id)
print "worker details:  " + str(details)


job_id = sw.postJob(project_id, name)
print "postJob returned:  " + str(ret)

print "About to sleep 20 to let job run..."
time.sleep(20)

logstr = sw.getLog(project_id, job_id)
print "sw.getLog returns:  " + str(logstr)

