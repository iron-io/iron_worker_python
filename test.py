from iron_worker import *
import unittest
from datetime import datetime
from datetime import timedelta


class TestIronWorker(unittest.TestCase):

    def setUp(self):
        self.code_name = "test_code"

        self.worker = IronWorker()

        self.package = CodePackage()
        self.package.merge("testDir", True)
        self.package.executable = "hello.py"
        self.worker.upload(self.package, name=self.code_name)

    def test_getCodeDetails(self):
        codes = self.worker.codes()

        code = self.worker.code(codes[0].id)
        self.assertEqual(codes[0].id, code.id)

    def test_postTask(self):
        payload = {
                "dict": {"a": 1, "b": 2},
                "var": "alpha",
                "list": ['apples', 'oranges', 'bananas']
        }
        resp = self.worker.queue(code_name=self.code_name, payload=payload)

        task_id = resp.id

        tasks = self.worker.tasks()
        task_ids = []
        for task in tasks:
            task_ids.append(task.id)

        self.assertIn(task_id, task_ids)

    def test_getTaskDetails(self):
        payload = {
                "dict": {"a": 1, "b": 2},
                "var": "alpha",
                "list": ['apples', 'oranges', 'bananas']
        }
        resp = self.worker.queue(code_name=self.code_name, payload=payload)

        task_id = resp.id

        tasks = self.worker.tasks()
        task_ids = []
        for task in tasks:
            task_ids.append(task.id)

        self.assertIn(task_id, task_ids)

        task = self.worker.task(resp)

        self.assertEqual(task_id, task.id)

    def test_zcancelTask(self):
        time.sleep(2)
        tasks = self.worker.tasks()
        for task in tasks:
            self.worker.cancel(task)

        time.sleep(3)
        new_tasks = self.worker.tasks()
        real_tasks = []
        for task in new_tasks:
            if task.status not in ['cancelled', 'error', 'killed']:
                real_tasks.append(task)

        self.assertEqual(len(real_tasks), 0)

    def test_postSchedule(self):
        resp = self.worker.queue(code_name=self.code_name, delay=120)

        schedules = self.worker.tasks()
        schedule_ids = []
        for schedule in schedules:
            schedule_ids.append(schedule.id)
    
        time.sleep(2)

        self.assertIn(resp.id, schedule_ids)

    def test_postScheduleAndPayload(self):
        resp = self.worker.queue(code_name=self.code_name, delay=120,
                        payload={"foo": "bar"})

        schedules = self.worker.tasks()
        schedule_ids = []
        for schedule in schedules:
            schedule_ids.append(schedule.id)

        time.sleep(2)

        self.assertIn(resp.id, schedule_ids)

    def test_postAdvancedSchedule(self):
        delta = timedelta(hours=1)
        start_at = datetime.now() + delta # one hour from now
        resp = self.worker.queue(
                code_name=self.code_name,
                payload={"schedule": "AWESOME SCHEDULE!"},
                start_at=start_at, run_every=3600, run_times=8)

        schedules = self.worker.tasks(scheduled=True)
        schedule_ids = []
        for schedule in schedules:
            schedule_ids.append(schedule.id)
    
        time.sleep(2)

        self.assertIn(resp.id, schedule_ids)

    def test_zcancelSchedule(self):
        schedules = self.worker.tasks(scheduled=True)

        for schedule in schedules:
            self.worker.cancel(schedule)

        new_schedules = self.worker.tasks(scheduled=True)
        real_schedules = []
        for schedule in new_schedules:
            if schedule.status not in ['cancelled', 'error']:
                real_schedules.append(schedule)

        self.assertEqual(len(real_schedules), 0)

    def test_zdeleteCode(self):
        codes = self.worker.codes()

        for code in codes:
            self.worker.deleteCode(code)

        new_codes = self.worker.codes()
        self.assertEqual(len(new_codes), 0)

if __name__ == '__main__':
    unittest.main()
