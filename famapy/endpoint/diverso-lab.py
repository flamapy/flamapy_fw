from typing import Any

import hug

from famapy.core.discover import DiscoverMetamodels
from famapy.core.plugins import Operations


dm = DiscoverMetamodels()


@hug.cli()
@hug.get('/get-plugins/', versions=1)
def get_plugins() -> dict[str, list[str]]:
    """ Get availables plugins """
    plugins = dm.get_plugins()
    return {'plugins': plugins}


@hug.cli()
@hug.get('/get-operations/{plugin}/')
def get_operations_by_plugin(plugin: str, versions: int = 1) -> dict[str, Operations]:
    """ Get availables operations gave a plugin name """
    operations = dm.get_operations_by_plugin(plugin)
    return {'operations': operations}


@hug.cli()
def use_operation(plugin: str, operation: str, filename: str, versions: int = 1) -> dict[str, Any]:
    """
    Execute an operation gave a plugin, an operation and one input file.
    - Read input model, transform and call operation
    """
    result = dm.use_operation_from_file(plugin, operation, filename)
    return {'result': result}


@hug.cli()
def use_operation_from_fm_file(
    plugin: str,
    operation: str,
    filename: str,
    versions: int = 1
) -> dict[str, Any]:
    """
    Execute an operation gave a plugin, an operation and one input fm file.
    - Read input model, transformations and call operation
    """
    result = dm.use_operation_from_fm_file(plugin, operation, filename)
    return {'result': result}
