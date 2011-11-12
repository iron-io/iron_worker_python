from simple_worker_pip import *
import unittest
import sys
import random
import string
import ConfigParser

class TestSimpleWorkerPip(unittest.TestCase):
  
  def setUp(self):
    config = ConfigParser.RawConfigParser()
    config.read('config.ini')
    self.token = config.get("IronWorker", "token")
    self.host= config.get("IronWorker", "host")
    self.port = config.get("IronWorker", "port")
    self.version = config.get("IronWorker", "version")

    self.sw = SimpleWorker(self.host, self.port, self.version, self.token)

  def test_create_project(self):
    projectName = "pip-gen-project-" + str(int(time.time()))
    newProjectID = self.sw.postProject(projectName)

    projects = self.sw.getProjects()

    project_names = []
    for project in projects: 
      project_names.append(project['name'])

    #self.assertIn(projectName, project_names)
    self.assertTrue(projectName in project_names)

  def test_delete_project(self):
    return
    projectName = "pip-gen-project-" + str(int(time.time()))
    newProjectID = self.sw.postProject(projectName)

    projects = self.sw.getProjects()
    self.sw.deleteProject(projects[0]['id'])

    projects = self.sw.getProjects()
    project_names = []
    for project in projects: 
      project_names.append(project['name'])
        
    self.assertTrue(projectName not in project_names)
 
if __name__ == '__main__':
  unittest.main()
