from typing import Any

import hug

from famapy.core.discover import DiscoverMetamodels
from famapy.core.exceptions import ConfigurationNotFound, OperationNotFound
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
    plugin: str,
    configuration: str,
    versions: int = 1
) -> OperationResult:
    """
    Execute an operation gave an operation and one input file. Optionally you
    can give a plugin as last parameter.
    """

    try:
        plg = plugin if plugin != "None" else None
        config = configuration if configuration != "None" else None

        result = dm.use_operation_from_file(
            operation, filename, plugin_name=plg, config_text=config)
        return OperationResult({'result': result})
    except OperationNotFound:
        return OperationResult({'error': 'Operation not found'})
    except FileNotFoundError:
        return OperationResult({'error': 'File not found'})
    except ConfigurationNotFound:
        return OperationResult({'error': 'Configuration not set'})
    except Exception:
        return OperationResult({'error': 'unexpected error'})
