import json
import iron_core

canned_tasks = '''{
    "tasks": [
        {
            "id": "4f3595381cf75447be029da5",
            "created_at": "2012-02-10T22:07:52.712Z",
            "updated_at": "2012-02-10T22:11:55Z",
            "project_id": "4f32d521519cb67829000390",
            "code_id": "4f32d9c81cf75447be020ea5",
            "status": "complete",
            "msg": "SetProgress output",
            "code_name": "MyWorker",
            "start_time": "2012-02-10T22:07:54Z",
            "end_time": "2012-02-10T22:11:55Z",
            "duration": 241441,
            "run_times": 1,
            "timeout": 3600,
            "percent": 100
        }
    ]
}'''

canned_shedules = '''{
    "schedules": [
        {
            "id": "4eb1b490cddb136065000011",
            "created_at": "2012-02-14T03:06:41Z",
            "updated_at": "2012-02-14T03:06:41Z",
            "project_id": "4eb1b46fcddb13606500000d",
            "msg": "Ran max times.",
            "status": "complete",
            "code_name": "MyWorker",
            "start_at": "2011-11-02T21:22:34Z",
            "end_at": "2262-04-11T23:47:16Z",
            "next_start": "2011-11-02T21:22:34Z",
            "last_run_time": "2011-11-02T21:22:51Z",
            "run_times": 1,
            "run_count": 1
        },
        {
            "id": "4eb1b490cddb136065000011",
            "created_at": "2012-02-14T03:06:41Z",
            "updated_at": "2012-02-14T03:06:41Z",
            "project_id": "4eb1b46fcddb13606500000d",
            "msg": "Ran max times.",
            "status": "complete",
            "code_name": "DifferentWorker",
            "start_at": "2011-11-02T21:22:34Z",
            "end_at": "2262-04-11T23:47:16Z",
            "next_start": "2011-11-02T21:22:34Z",
            "last_run_time": "2011-11-02T21:22:51Z",
            "run_times": 1,
            "run_count": 1
        }
    ]
}'''

canned_data = {
    'tasks': dict(body=json.loads(canned_tasks)),
    'tasks?code_name=MyWorker': dict(body=json.loads(canned_tasks)),
    'schedules': dict(body=json.loads(canned_shedules))
}

class FakeIronClient(iron_core.IronClient):
    '''Monkey-patches the iron_client.__init__ so that the logon can be bypassed'''
    def __init__(self, *args, **kwargs):
        pass

def stub(*args, **kwargs):
    '''Provides a indirect input to the system under test
    http://xunitpatterns.com/Test%20Stub.html
    '''
    return canned_data.get(args[0], None)

def spy(*args, **kwargs):
    '''Provides a test spy to verify the indirect output of the system under test
    http://xunitpatterns.com/Test%20Spy.html
    '''
    spy.data = args
    return stub(*args, **kwargs)
    
def remove_spy_data():
    if hasattr(spy,'data'):
        del spy.data

__all__ = [FakeIronClient.__name__, stub.__name__, spy.__name__, remove_spy_data.__name__]