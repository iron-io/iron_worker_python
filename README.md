iron_worker_python is Python language binding for IronWorker.

IronWorker is a massively scalable background processing system.
[See How It Works](http://www.iron.io/products/worker/how)

# Getting Started


## Get credentials
To start using iron_worker_php, you need to sign up and get an oauth token.

1. Go to http://iron.io/ and sign up.
2. Get an Oauth Token at http://hud.iron.io/tokens

## Install iron_worker_python
Just copy ```iron_worker.py``` and ```poster``` and include iron_worker.py in your script:

```python
from iron_worker import *
```
## Configure
Two ways to configure IronWorker:

* Specifying options when constructing the binding:

```python
worker = IronWorker(token='XXXXXXXXXX', project_id='xxxxxxxxxxx')
```

* Passing an ini file name which stores your configuration options. Rename sample_config.ini to config.ini and include your Iron.io credentials (`token` and `project_id`):

```python
worker = IronWorker(config='config.ini')
```

## Creating a Worker

Here's an example worker:

```python
print "Hello PYTHON World!\n"
```

## Upload code to server

* Zip worker:

```python
# Zip single file:
IronWorker.createZip(destination="worker.zip", files=['HelloWorld.py'], overwrite=True)
# OR
# Zip whole directory:
IronWorker.zipDirectory(directory="hello_world/", destination='worker.zip', overwrite=True)
```

* Submit worker:

```python
res = worker.postCode(runFilename='HelloWorld.py', zipFilename='worker.zip', name='HelloWorld')
```

Where 'HelloWorld' is a worker name which should be used later for queueing and sheduling.

## Queueing a Worker

```python
task_id = worker.postTask(name='HelloWorld')
```

Worker should start in a few seconds.

## Scheduling a Worker
If you want to run your code at a delay, you should schedule it:

```python
# 3 minutes from now
start_at =  3*60
worker.postSchedule(name='HelloWorld', delay=start_at)
```

## Status of a Worker
To get the status of a worker, you can use the ```getTaskDetails()``` method.

```python
task_id = worker.postTask('HelloWorld')
details = worker.getTaskDetails(task_id=task_id);

print details['status'] # prints 'queued', 'complete', 'error' etc.
```

## Get Worker Log

Use any function that print text inside your worker to put messages to log.

```python
import time
task_id = worker.postTask('HelloWorld')
time.sleep(10)
details = worker.getTaskDetails(task_id)
# Check log only if task is finished.
if details['status'] != 'queued':
    log = worker.getLog(task_id);
    print log # prints "Hello PHP World!"
```

## Loading the Task Data Payload

To provide Payload to your worker simply put a dict with any content you want.

```python
payload = {
    'key_one': 'Helpful text',
    'key_two': 2,
    'options': ['option 1', 'option 2']
}

worker.postTask(name='HelloWorld', payload=payload)
```

When your code is executed, it will be passed three program arguments:

* **-id** - The task id.
* **-payload** - the filename containing the data payload for this particular task.
* **-d** - the user writable directory that can be used while running your job.

# Full Documentation

You can find more documentation here:

* http://docs.iron.io Full documetation for iron.io products.
* [IronWorker Python Wiki pages](https://github.com/iron-io/iron_worker_python/wiki).
