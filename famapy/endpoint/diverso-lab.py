from typing import Any, Optional

import hug

from famapy.core.discover import DiscoverMetamodels
from famapy.core.exceptions import OperationNotFound
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
@hug.get('/use-operation-from-file/{operation}/{filename}/')
def use_operation_from_file(
    operation: str,
    filename: str,
    plugin: Optional[str] = None,
    versions: int = 1
) -> OperationResult:
    """
    Execute an operation gave an operation and one input file. Optionally you
    can give a plugin as last parameter.
    """
    try:
        result = dm.use_operation_from_file(operation, filename, plugin)
        return OperationResult({'result': result})
    except OperationNotFound:
        return OperationResult({'result': 'Operation not found'})
    except FileNotFoundError:
        return OperationResult({'result': 'File not found'})
    except Exception:
        return OperationResult({'result': 'unexpected error'})
