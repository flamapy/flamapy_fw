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
git clone git@github.com:FaMaPy/fm_metamodel.git
git clone git@github.com:FaMaPy/pysat_metamodel.git
```

You can install it inside the same virtualenv environment with:

```
pip install -e .
```


## Review code quality and styles error

```
prospector
```
