from setuptools import setup

setup(
        name='iron-worker',
        py_modules=["iron_worker"],
	packages=["testDir"],
        version='1.1.0',
        install_requires=["iron_core", "python-dateutil"],
        description='The Python client for IronWorker, a cloud service for background processing.',
        author='Iron.io',
        author_email="support@iron.io",
        url='https://www.github.com/iron-io/iron_worker_python',
        keywords=['iron', 'ironio', 'iron.io', 'iron-io', 'ironworker', 'iron-worker', 'iron_worker', 'worker', 'cloud', 'task queue', 'background processing'],
        classifiers = [
                "Programming Language :: Python",
                "Programming Language :: Python :: 3",
                "Intended Audience :: Developers",
                "Operating System :: OS Independent",
                "Development Status :: 2 - Pre-Alpha",
                "License :: OSI Approved :: BSD License",
                "Natural Language :: English",
                "Topic :: Internet",
                "Topic :: Internet :: WWW/HTTP",
                "Topic :: Software Development :: Libraries :: Python Modules",

        ],
        long_description="""IronWorker Python Library
-------------------------

This package offers a client interface to the Iron.io IronWorker service. It 
offers a full, native interface to the IronWorker API, including creating 
and uploading code package, queuing and scheduling tasks, viewing task logs, 
and more.

IronWorker is a background processing and task queuing system that lets your 
applications use the cloud to do their heavy lifting. Find out more at 
http://www.iron.io/products/worker."""
)
