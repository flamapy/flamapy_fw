from typing import Any, NewType, Optional
import argparse
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


def get_plugins() -> PluginsType:
    """Get available plugins"""
    plugins = dm.get_plugins()
    return PluginsType({'plugins': plugins})


def get_operations_name_by_plugin(plugin: str) -> OperationDict:
    """Get available operations given a plugin name"""
    operations = dm.get_name_operations_by_plugin(plugin)
    return OperationDict({'operations': operations})


def use_operation_from_file(
    operation: str,
    filename: str,
    plugin: Optional[str] = None,
    configuration_file: Optional[str] = None,
) -> OperationResult:
    """
    Execute an operation given an operation and one input file. Optionally, you
    can give a plugin as the last parameter.
    """
    try:
        result = dm.use_operation_from_file(operation, filename, plugin, configuration_file)
        return OperationResult({'result': result})
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


def main():
    parser = argparse.ArgumentParser(description="A simple CLI example")
    subparsers = parser.add_subparsers(dest='command', help='sub-command help')

    # Subparser for the 'get-plugins' command
    parser_plugins = subparsers.add_parser('get-plugins', help='Get available plugins')

    # Subparser for the 'get-operations' command
    parser_operations = subparsers.add_parser('get-operations', help='Get available operations by plugin')
    parser_operations.add_argument('plugin', type=str, help='Name of the plugin')

    # Subparser for the 'use-operation' command
    parser_use_operation = subparsers.add_parser('use-operation', help='Use an operation from file')
    parser_use_operation.add_argument('operation', type=str, help='Operation to perform')
    parser_use_operation.add_argument('filename', type=str, help='File to use for the operation')
    parser_use_operation.add_argument('--plugin', type=str, help='Optional plugin name')
    parser_use_operation.add_argument('--configuration_file', type=str, help='Optional configuration file')

    args = parser.parse_args()

    if args.command == 'get-plugins':
        result = get_plugins()
        print(result)
    elif args.command == 'get-operations':
        result = get_operations_name_by_plugin(args.plugin)
        print(result)
    elif args.command == 'use-operation':
        result = use_operation_from_file(args.operation, args.filename, args.plugin, args.configuration_file)
        print(result)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
