from nose.tools import *

from toolbox import *

import iron_core
# Monkey Patching IronClient so that I can skip authentication
iron_core.IronClient = FakeIronClient
from iron_worker import IronWorker

@with_setup(teardown=remove_spy_data)
def test_iron_worker_finds_tasks():
    '''IronWorker: Can find tasks without their names (Regression Test)'''
    worker = IronWorker()
    worker.client.get = stub
    tasks = worker.tasks()
    assert_equal(len(tasks), 1)

@with_setup(teardown=remove_spy_data)
def test_iron_worker_finds_sheduled_tasks():
    '''IronWorker: Can find sheduled tasks without their names (Regression Test)'''
    worker = IronWorker()
    worker.client.get = stub
    scheduled_tasks = worker.tasks(scheduled=1)
    assert_equal(len(scheduled_tasks), 2)

@with_setup(teardown=remove_spy_data)
def test_iron_worker_api_call_without_parameter_1():
    '''IronWorker: Calls the rest api as usual, when there is no code_name given (default parameter)'''
    worker = IronWorker()
    worker.client.get = spy
    tasks = worker.tasks()
    assert_equal(len(tasks), 1)
    assert_equal(spy.data, ('tasks',))

@with_setup(teardown=remove_spy_data)
def test_iron_worker_api_call_without_parameter_2():
    '''IronWorker: Calls the rest api as usual, when there is no code_name given (empty string)'''
    worker = IronWorker()
    worker.client.get = spy
    tasks = worker.tasks(code_name="")
    assert_equal(len(tasks), 1)
    assert_equal(spy.data, ('tasks',))

@with_setup(teardown=remove_spy_data)
def test_iron_worker_api_call_with_code_name_parameter():
    '''IronWorker: Calls the rest api with the code_name parameter set'''
    worker = IronWorker()
    worker.client.get = spy
    tasks = worker.tasks(code_name="MyWorker")
    assert_equal(len(tasks), 1)
    assert_equal(spy.data, ('tasks?code_name=MyWorker',))

@with_setup(teardown=remove_spy_data)
def test_iron_worker_call_for_scheduled_tasks():
    '''IronWorker: Calls the rest api for scheduled tasks normally'''
    worker = IronWorker()
    worker.client.get = spy
    scheduled_tasks = worker.tasks(scheduled=1)
    assert_equal(len(scheduled_tasks), 2)
    assert_equal(spy.data, ('schedules',))

@with_setup(teardown=remove_spy_data)
def test_iron_worker_call_for_scheduled_tasks_with_filter():
    '''IronWorker: Calls the rest api for scheduled tasks normally but filters the results afterwards'''
    ONLY_ONE = 1
    worker = IronWorker()
    worker.client.get = spy
    scheduled_tasks = worker.tasks(scheduled=1, code_name="MyWorker")
    assert_equal(len(scheduled_tasks), ONLY_ONE)