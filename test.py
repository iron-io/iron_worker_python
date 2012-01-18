from iron_worker import *
import unittest
import ConfigParser
import time


class TestIronWorkerPip(unittest.TestCase):

    def setUp(self):
        config = ConfigParser.RawConfigParser()
        config.read('config.ini')
        self.token = config.get("IronWorker", "token")
        self.host = config.get("IronWorker", "host")
        self.port = config.get("IronWorker", "port")
        self.version = config.get("IronWorker", "version")
        self.project_id = config.get("IronWorker", "project_id")
        self.new_project_id = "New Project Id"

        self.code_name = "test%d" % time.time()

        self.worker = IronWorker(token=self.token, host=self.host,
            port=self.port, version=self.version, project_id=self.project_id)

        IronWorker.createZip(destination="test.zip", files=["test.py"],
                overwrite=True)
        response = self.worker.postCode(name=self.code_name,
                runFilename="test.py", zipFilename="test.zip")


    def test_setProject(self):
        self.assertNotEqual(self.worker.project_id, self.new_project_id)

        self.worker.setProject(self.new_project_id)
        self.assertEqual(self.worker.project_id, self.new_project_id)

        self.worker.setProject(self.project_id)
        self.assertEqual(self.worker.project_id, self.project_id)

    def test_headers(self):
        self.assertEqual(self.worker.headers['Accept'], "application/json")
        self.assertEqual(self.worker.headers['Accept-Encoding'],
                "gzip, deflate")
        self.assertEqual(self.worker.headers['User-Agent'],
                "IronWorker Python Pip v0.3")

    def test_postCode(self):
        IronWorker.createZip(destination="test.zip", files=["test.py"],
                overwrite=True)
        response = self.worker.postCode(name=self.code_name,
                runFilename="test.py", zipFilename="test.zip")
        self.assertEqual(response['status_code'], 200)

        codes = self.worker.getCodes()
        code_names = []
        for code in codes:
            code_names.append(code["name"])
        self.assertIn(self.code_name, code_names)

    def test_getCodeDetails(self):
        IronWorker.createZip(destination="test.zip", files=["test.py"],
                overwrite=True)
        response = self.worker.postCode(name=self.code_name,
                runFilename="test.py", zipFilename="test.zip")
        self.assertEqual(response['status_code'], 200)

        codes = self.worker.getCodes()

        code = self.worker.getCodeDetails(code_id=codes[0]['id'])
        self.assertEqual(codes[0]['id'], code['id'])

    def test_postTask(self):
        payload = {
                "dict": {"a": 1, "b": 2},
                "var": "alpha",
                "list": ['apples', 'oranges', 'bananas']
        }
        resp = self.worker.postTask(name=self.code_name, payload=payload)

        self.assertEqual(resp['status_code'], 200)
        self.assertEqual(len(resp['tasks']), 1)

        task_id = resp['tasks'][0]['id']

        tasks = self.worker.getTasks()
        task_ids = []
        for task in tasks:
            task_ids.append(task['id'])

        self.assertIn(task_id, task_ids)

    def test_getTaskDetails(self):
        payload = {
                "dict": {"a": 1, "b": 2},
                "var": "alpha",
                "list": ['apples', 'oranges', 'bananas']
        }
        resp = self.worker.postTask(name=self.code_name, payload=payload)

        self.assertEqual(resp['status_code'], 200)
        self.assertEqual(len(resp['tasks']), 1)

        task_id = resp['tasks'][0]['id']

        tasks = self.worker.getTasks()
        task_ids = []
        for task in tasks:
            task_ids.append(task['id'])

        self.assertIn(task_id, task_ids)

        tasks = self.worker.getTasks()
        task_id = tasks[0]['id']

        task = self.worker.getTaskDetails(task_id=task_id)

        self.assertEqual(task_id, task['id'])

    def test_deleteTask(self):
        tasks = self.worker.getTasks()

        for task in tasks:
            self.worker.deleteTask(task_id=task['id'])

        new_tasks = self.worker.getTasks()
        real_tasks = []
        for task in new_tasks:
            if task['status'] not in ['cancelled', 'error']:
                real_tasks.append(task)
        self.assertEqual(len(real_tasks), 0)

    def test_postSchedule(self):
        schedule_id = self.worker.postSchedule(name=self.code_name, delay=120)

        schedules = self.worker.getSchedules()
        schedule_ids = []
        for schedule in schedules:
            schedule_ids.append(schedule['id'])

        self.assertIn(schedule_id, schedule_ids)

    def test_deleteSchedule(self):
        schedules = self.worker.getSchedules()

        for schedule in schedules:
            self.worker.deleteSchedule(schedule_id=schedule['id'])

        new_schedules = self.worker.getSchedules()
        real_schedules = []
        for schedule in new_schedules:
            if schedule['status'] not in ['cancelled', 'error']:
                real_schedules.append(schedule)

        self.assertEqual(len(real_schedules), 0)

    def test_deleteCode(self):
        codes = self.worker.getCodes()

        for code in codes:
            self.worker.deleteCode(code_id=code['id'])

        new_codes = self.worker.getCodes()
        self.assertEqual(len(new_codes), 0)

if __name__ == '__main__':
    unittest.main()
