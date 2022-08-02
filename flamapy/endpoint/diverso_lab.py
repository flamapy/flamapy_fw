from typing import Any, NewType, Optional

import hug
from flamapy.core.discover import DiscoverMetamodels
from flamapy.core.exceptions import (
    ConfigurationNotFound,
    OperationNotFound,
    PluginNotFound,
    TransformationNotFound,
)

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
    except OperationNotFound:
        return OperationResult({'Error': 'Operation not found'})
    except PluginNotFound:
        return OperationResult({'Error': 'Plugin not found'})
    except TransformationNotFound:
        return OperationResult({'Error': 'Transformation not found'})
    except FileNotFoundError:
        return OperationResult({'Error': 'File not found'})
    except ConfigurationNotFound:
        return OperationResult({'Error': 'Configuration file not found'})
    except Exception:
        return OperationResult({'Error': 'Unexpected error'})

    return OperationResult({'result': result})
