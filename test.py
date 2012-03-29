from iron_worker import *
import unittest
import time


class TestIronWorker(unittest.TestCase):

    def setUp(self):
        self.code_name = "test%d" % time.time()
        self.worker = IronWorker(config="config.ini")

        IronWorker.zipDirectory(destination="test.zip", overwrite=True,
                directory="testDir")
        response = self.worker.postCode(name=self.code_name,
                runFilename="hello.py", zipFilename="test.zip")

    def test_postCode(self):
        IronWorker.createZip(destination="test.zip", overwrite=True,
                files=["hello.py"])
        response = self.worker.postCode(name=self.code_name,
                runFilename="hello.py", zipFilename="test.zip")
        self.assertEqual(response['status_code'], 200)

        codes = self.worker.getCodes()
        code_names = []
        for code in codes:
            code_names.append(code["name"])
        self.assertIn(self.code_name, code_names)

    def test_postZip(self):
        IronWorker.zipDirectory(directory="testDir", destination="test.zip",
                overwrite=True)
        response = self.worker.postCode(name=self.code_name,
                runFilename="hello.py", zipFilename="test.zip")
        self.assertEqual(response['status_code'], 200)

        codes = self.worker.getCodes()

        code = self.worker.getCodeDetails(code_id=codes[0]['id'])
        self.assertEqual(codes[0]['id'], code['id'])

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

    def test_cancelTask(self):
        tasks = self.worker.getTasks()

        for task in tasks:
            self.worker.cancelTask(task_id=task['id'])

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

    def test_postScheduleAndPayload(self):
        schedule_id = self.worker.postSchedule(name=self.code_name, delay=120,
                        payload={"foo": "bar"})

        schedules = self.worker.getSchedules()
        schedule_ids = []
        for schedule in schedules:
            schedule_ids.append(schedule['id'])

        self.assertIn(schedule_id, schedule_ids)

    def test_postAdvancedSchedule(self):
        start_at = time.gmtime(time.time() + 3600)  # one hour from now
        schedule_id = self.worker.postSchedule(
                name="advanced_%s" % self.code_name,
                payload={"schedule": "AWESOME SCHEDULE!"},
                code_name=self.code_name, start_at=start_at, run_every=3600,
                run_times=8)

        schedules = self.worker.getSchedules()
        schedule_ids = []
        for schedule in schedules:
            schedule_ids.append(schedule['id'])

        self.assertIn(schedule_id, schedule_ids)

    def test_cancelSchedule(self):
        schedules = self.worker.getSchedules()

        for schedule in schedules:
            self.worker.cancelSchedule(schedule_id=schedule['id'])

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
