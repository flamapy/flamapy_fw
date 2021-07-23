from typing import Any

import hug

from famapy.core.discover import DiscoverMetamodels
from typing import NewType


dm = DiscoverMetamodels()

PluginsType = NewType('PluginsType', dict[str, list[str]])
OperationDict = NewType('OperationDict', dict[str, list[str]])
OperationResult = NewType('OperationResult', dict[str, Any])


@hug.cli()
@hug.get('/get-plugins/', versions=1)
def get_plugins() -> PluginsType:
    """ Get availables plugins """
    plugins = dm.get_plugins()
    return PluginsType({'plugins': plugins})


@hug.cli()
@hug.get('/get-operations/{plugin}/')
def get_operations_name_by_plugin(plugin: str, versions: int = 1) -> OperationDict:
    """ Get availables operations gave a plugin name """
    operations = dm.get_name_operations_by_plugin(plugin)
    return OperationDict({'operations': operations})


@hug.cli()
def use_operation(plugin: str, operation: str, filename: str, versions: int = 1) -> OperationResult:
    """
    Execute an operation gave a plugin, an operation and one input file.
    - Read input model, transform and call operation
    """
    result = dm.use_operation_from_file(plugin, operation, filename)
    return OperationResult({'result': result})


@hug.cli()
def use_operation_from_fm_file(
    operation: str,
    filename: str,
    versions: int = 1
) -> dict[str, Any]:
    """
    Execute an operation gave an operation and one input file.
    - Read input model, t2m and several transformations for reach operation
    """
    result = dm.use_operation_from_fm_file(operation, filename)
    return {'result': result}
