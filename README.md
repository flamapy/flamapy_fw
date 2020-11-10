# famapy-core

FaMaPy is a Python-based AAFM framework that takes into consideration previous AAFM tool designs and enables multi-solver and multi-metamodel support for the integration of AAFM tooling on the Python ecosystem.

The main features of the framework are:
* Easy to extend by enabling the creation of new plugins following a semi-automatic generator approach.
* Support multiple variability models. Currently, it provides support for cardinality-based feature models. However, it is easy to integrate others such as attributed feature models
* Support multiple solvers. Currently, it provides support for the PySAT metasolver, which enables more than ten different solvers.
* Support multiple operations. It is developed, having in mind multi-model operations such as those depicted by Familiar  and single-model operations.


## Installation

Pypi: https://pypi.org/project/famapy/

```
pip install famapy
```

Source: https://github.com/diverso-lab/core

```
git clone https://github.com/diverso-lab/core
python setup.py install
```

IMPORTANT NOTE: this repository not work without metamodels, you need to install some metamodels

You can take a look to the execution at:

[![asciicast](https://asciinema.org/a/366394.svg)](https://asciinema.org/a/366394)

## Execute tests

Execute test with install package:

```
pip install pytest
python -m pytest
```

Execute test with module installed:

```
pip install -e .
pytest
```

## Usage

### Create new plugins with the provide generator tool

FaMaPy framework provides a tools to generate structure for new plugins.

The tools is `famapy_admin.py`

You can create a new plugins with the next command:

```
famapy_admin.py --path PLUGIN_PATH NAME_PLUGIN EXTENSION_PLUGIN
# Example
famapy_admin.py --path /home/user/famapy-plugin1 plugin1 plug1
```

### Install existing plugins

The known plugins that you can install with pip are:

```
famapy-fm
famapy-sat
```

NOTE: If you have a new plugins and this plugins not appear in previous list, you can send a PR to add it.


### Command line CLI and HTTP API

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

### Manual operations and transformations from installed plugins

FaMaPy provides a discover to facilitate the operations with the installed plugins

IMPORTANT NOTE: this repository not work without metamodels, you need to install some metamodels

You can take a look to the execution at:

[![asciicast](https://asciinema.org/a/366394.svg)](https://asciinema.org/a/366394)



## Development

### Run tests

With the module installed, you can execute:

```
pytest
```


### Install/test metamodels

There is at the moment two separate metamodels repository:

```
git clone git@github.com:diverso-lab/fm_metamodel.git
git clone git@github.com:diverso-lab/pysat_metamodel.git
```

You can install it inside the same virtualenv environment with:

```
pip install -e .
```


### Review code quality and styles error

```
prospector
```

## Changelog

Detailed changes for each release are documented in the [release notes](https://github.com/diverso-lab/core/releases)


## Contributing

See [CONTRIBUTING.md](https://github.com/diverso-lab/core/blob/master/CONTRIBUTING.md)
