# Famapy
FaMaPy is a Python-based AAFM framework that takes into consideration previous AAFM tool designs and enables multi-solver and multi-metamodel support for the integration of AAFM tooling on the Python ecosystem.

The main features of the framework are:
* Easy to extend by enabling the creation of new plugins following a semi-automatic generator approach.
* Support multiple variability models. Currently, it provides support for cardinality-based feature models. However, it is easy to integrate others such as attributed feature models
* Support multiple solvers. Currently, it provides support for the PySAT metasolver, which enables more than ten different solvers.
* Support multiple operations. It is developed, having in mind multi-model operations such as those depicted by Familiar  and single-model operations.

## Available plugins
[famapy-fm](https://github.com/diverso-lab/fm_metamodel)
[famapy-sat](https://github.com/diverso-lab/pysat_metamodel)

## Documentation

All the proyect related documentation can be found in wiki format at [wiki](https://github.com/diverso-lab/core/wiki)

## Changelog
Detailed changes for each release are documented in the [release notes](https://github.com/diverso-lab/core/releases)

## Contributing

See [CONTRIBUTING.md](https://github.com/diverso-lab/core/blob/master/CONTRIBUTING.md)
