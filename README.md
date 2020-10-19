# core

This repo will host the core components of FaMaPy


## Install development

Create virtualenv and install setup.py:

```
python3 -m venv env .
source env/bin/activate
pip install -e .  # Install package in development mode
```

IMPORTANT NOTE: this repository not work without metamodels, you need to install some metamodels


## Execute tests

After you install the module, you can execute:


```
pytest
```


## Install metamodels

There is at the moment two separate metamodels repository:

```
git clone git@github.com:diverso-lab/fm_metamodel.git
git clone git@github.com:diverso-lab/pysat_metamodel.git
```

You can install it inside the same virtualenv environment with:

```
pip install -e .
```


## Review code quality and styles error

```
prospector
```


## Command line CLI and HTTP API

With the hug python library, we have created two different endpoints:

* Command line CLI
* HTTP API

For execute the command line:

```
hug -f famapy/endpoint/diverso-lab.py -c help
# Example
hug -f famapy/endpoint/diverso-lab.py -c get_plugins
hug -f famapy/endpoint/diverso-lab.py -c get_operations_by_plugin
hug -f famapy/endpoint/diverso-lab.py -c use_operation_from_fm_file famapy.metamodels.pysat_metamodel Valid test.xml
```

For execute the HTTP API:

```
hug -f famapy/endpoint/diverso-lab.py  # mount the endpoint in port 8000
# Doc: hug generate doc in json when you access to no exist endpoint
http://localhost:8000/example/
# Example
http://localhost:8000/v1/get-plugins/
http://localhost:8000/v1/get-operations/famapy.metamodels.pysat_metamodel/
```

Extra: If you want expose your api at the world, you can use ngrok:

```
ngrok http 8000
```
