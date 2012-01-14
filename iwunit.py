from iron_worker_pip import *
import unittest
import sys
import random
import string
import ConfigParser

class TestIronWorkerPip(unittest.TestCase):
  
  def setUp(self):
    config = ConfigParser.RawConfigParser()
    config.read('config.ini')
    self.token = config.get("IronWorker", "token")
    self.host= config.get("IronWorker", "host")
    self.port = config.get("IronWorker", "port")
    self.version = config.get("IronWorker", "version")

    self.worker = IronWorker(self.token, self.host, self.port, self.version)

  def test_create_project(self):
    projectName = "pip-gen-project-" + str(int(time.time()))
    newProjectID = self.worker.postProject(projectName)

    projects = self.worker.getProjects()

    project_names = []
    for project in projects: 
      project_names.append(project['name'])

    #self.assertIn(projectName, project_names)
    self.assertTrue(projectName in project_names)

  def test_delete_project(self):
    return
    projectName = "pip-gen-project-" + str(int(time.time()))
    newProjectID = self.worker.postProject(projectName)

    projects = self.worker.getProjects()
    self.worker.deleteProject(projects[0]['id'])

    projects = self.worker.getProjects()
    project_names = []
    for project in projects: 
      project_names.append(project['name'])
        
    self.assertTrue(projectName not in project_names)
 
if __name__ == '__main__':
  unittest.main()
