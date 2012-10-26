iron_worker_python is Python language binding for IronWorker.

IronWorker is a massively scalable background processing system.
[See How It Works](http://www.iron.io/products/worker/how).

# Getting Started


## Get credentials
To start using iron_worker_python, you need to sign up and get an OAuth token.

1. Go to http://iron.io/ and sign up.
2. Get an OAuth Token at http://hud.iron.io/tokens

## Install iron_worker_python

The recommended way to install iron_worker_python is through `pip` or `easy_install`. The package name is [iron-worker](http://pypi.python.org/pypi/iron-worker):

```
$ easy_install iron-worker
```

For `pip`:

```
$ pip install iron-worker
```

If you don't want to use `pip` or `easy_install`, you can always install from source. First, you'll need [iron_core_python](https://github.com/iron-io/iron_core_python). Download that; the file you're after is named iron_core.py. Then, download the [iron_worker_python](https://github.com/iron-io/iron_worker_python) library. The file you're after is named iron_worker.py. As long as both iron_core.py and iron_worker.py are in a directory in the import path, you're all set.

Including the library is easy:

```python
from iron_worker import *
```
## Configure

iron_worker_python follows the [standard configuration](http://dev.iron.io/worker/reference/configuration) convention followed by the other official libraries.

Create a file in the root of your project named "iron.json". You'll need your project ID and OAuth token. You can get them from [the HUD](https://hud.iron.io). Include them in the iron.json file as follows:

```
{
  "project_id": "Your_Project_ID",
  "token": "Your_OAuth_Token"
}
```

## Creating a Worker

Workers are just Python scripts that are run in the IronWorker cloud. Write them the way you would write any Python script.

Here's an example worker:

```python
print "Hello Python World!\n"
```

## Upload code to IronWorker

Uploading code to the server is done by creating a code package and uploading it. Creating a code package is simple:

```python
code = CodePackage(name="WorkerName")
code.merge("/path/to/file")
code.executable = "/path/to/file"
```

Every code package needs a name (which we specified above by passing it to the constructor, but we could have just as easily set it with `code.name = "WorkerName"`) and an executable (which we set using `code.executable` above, but could have just as easily passed it to the constructor). The executable is just the file you want the worker to run; it is the entry point for your code, the file you would execute if you were going to run the worker on your own machine.

iron_worker_python tries to react intelligently to your input; in the example above, it would have noticed that there is only one file in the CodePackage, and would have set it to be the executable. You should not rely on this, however; it's recommended that you always set the executable manually.
 
Once you have a CodePackage, you need to upload it using the API.

```python
worker = IronWorker() # Instantiate the API
worker.upload(code) # upload the CodePackage
```

Note that, for brevity, you can build simple CodePackages and upload them all in one step:

```python
worker = IronWorker() # Instantiate the API
worker.upload(target="/path/to/file/or/dir", name="WorkerName", executable="/path/to/executable")
```

This will create a CodePackage, merge in the target, set the name to "WorkerName", and set the executable to "/path/to/executable".

## Queueing a Task

To run your code, you need to queue a task against it.

```python
worker = IronWorker()
task = worker.queue(code_name="HelloWorld")
```

That will queue a task against the CodePackage with the name "HelloWorld". To pass a [payload](http://dev.iron.io/worker/payloads), just pass the data to `worker.queue`. It will be JSON-serialised and passed into your worker at runtime:

```python
worker = IronWorker()
task = worker.queue(code_name="HelloWorld", payload={"fruits": ["apples", "oranges", "bananas"], "best_song_ever": "Call Me Maybe"})
```

If you'd like to reuse Tasks or do more complex things with them, you can also instantiate them as instances of the `Task` class, then pass them to `worker.queue` method (this is actually what `worker.queue` is doing, transparently):

```python
worker = IronWorker()
task = Task(code_name="HelloWorld")
task.payload = {
    "fruits": ["apples", "oranges", "bananas"],
    "best_song_ever": "Call Me Maybe"
}
response = worker.queue(task)
```

If you'd like to, you can even set your task to run after a delay:

```python
task = Task(code_name="HelloWorld")
task.payload = {
    "fruits": ["apples", "oranges", "bananas"],
    "best_song_ever": "Call Me Maybe"
}
task.delay = 300 # start this task in 300 seconds (5 minutes)
response = worker.queue(task)
```

## Scheduling a Task

If you'd like to run a task at a specific time, or set a task to be run repeatedly, you want to create a [scheduled task](http://dev.iron.io/worker/scheduling). Unlike previous versions of iron_worker_python, we've unified tasks and scheduled tasks into the same interface. iron_worker_python will automatically detect when you want to create a scheduled task and react accordingly.

```python
task = Task(code_name="HelloWorldRepeating")
task.payload = {
    "fruits": ["apples", "oranges", "bananas"],
    "best_song_ever": "Call Me Maybe"
}
task.run_every = 300 # The task will run every 300 seconds (5 minutes)
response = worker.queue(task)
```

Likewise, if you'd like to run a task at a specific time, doing so is easy. Just pass a `datetime.datetime` object:

```python
task = Task(code_name="HelloFuture")
task.start_at = datetime.now() + timedelta(hours=1) # start tomorrow
response = worker.queue(task)
```

## Status of a Worker
To get the status of a worker, you can use the `worker.task` method.

```python
task = worker.queue('HelloWorld')
details = worker.task(task)

print details.status # prints 'queued', 'complete', 'error' etc.
```

If you don't have an instance of `Task`, you can also pass in the task ID. Note that if you do this, however, and you are attempting to retrieve that status of a scheduled task, you need to declare that as well:

```python
task = worker.queue("HelloWorld")
details = worker.task(id=task.id)

print details.status

scheduled_task = worker.queue("HelloWorld", run_every=60, run_count=3) # run this task 3 times, once a minute
scheduled_details = worker.task(scheduled_task.id, scheduled=True)
print scheduled_details.status
```

## Get Worker Log

Use any function that prints text inside your worker to insert messages into you worker's log. To retrieve a worker's log, use the `worker.log` method.

```python
task = worker.queue('HelloWorld')
time.sleep(10)
print worker.log(task)
```

If you don't have an instance of the `Task` object handy, you can also just use the ID of the task:

```python
task = worker.queue('HelloWorld')
time.sleep(10)
print worker.log(id=task.id)
```

## Loading the Task Data Payload

When your code is executed, it will be passed three program arguments:

* **-id** - The task id.
* **-payload** - the filename containing the data payload for this particular task.
* **-d** - the user writable directory that can be used while running your job.

Simply open the filename passed by `-payload`, read its contents, and (if you used iron_worker_python to queue the task), decode the string as JSON:

```python
payload = None
payload_file = None
for i in range(len(sys.argv)):
    if sys.argv[i] == "-payload" and (i + 1) < len(sys.argv):
        payload_file = sys.argv[i]
        break

f = open(payload_file, "r")
contents = f.read()
f.close()

payload = json.loads(contents)
```

# Full Documentation

You can find more documentation here:

* [Iron.io Dev Center](http://dev.iron.io): Full documentation for Iron.io products.
* [Example Workers](https://github.com/iron-io/iron_worker_examples)
