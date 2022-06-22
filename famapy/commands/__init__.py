#!/usr/bin/python

import argparse
import os
import sys
from shutil import copytree

from hug import development_runner


def parser() -> argparse.ArgumentParser:
    main_parser = argparse.ArgumentParser()
    subparser = main_parser.add_subparsers(title="commands", dest="command")

    new_plugin = subparser.add_parser("new_plugin", help="new_plugin")
    new_plugin.add_argument('name', type=str, help='A name for your plugin. Ex: fama')
    new_plugin.add_argument('extension', type=str, help='A extension for your plugin. Ex: fm')
    new_plugin.add_argument('--path', default='.', type=str, help='Plugin project path.')

    subparser.add_parser("cli", help="cli", description='famapy_admin.py api: command line api')
    return main_parser


def cmd_new_plugin(options: argparse.Namespace) -> None:
    name = options.name
    ext = options.extension
    dst = options.path
    src = 'skel_metamodel/'

    # Check DST exist
    if not os.path.isdir(dst):
        print(f"Folder {dst} not exist")
        sys.exit()

    # Check DST is empty
    if len(os.listdir(dst)) != 0:
        print(f"Folder {dst} is not empty")
        sys.exit()

    # Check DST has permissions to WRITE
    if not os.access(dst, os.W_OK):
        print(f"Folder {dst} has not write permissions")
        sys.exit()

    # Generating structure
    print("Generating structure ...")

    copy_files = copytree(src, dst)

    for copy_file in copy_files:
        with open(copy_file, "r", encoding="utf-8") as file:
            lines = file.readlines()
        with open(copy_file, "w", encoding="utf-8") as filewrite:
            for line in lines:
                out_line = line.replace('__NAME__', name.capitalize()).replace('__EXT__', ext)
                filewrite.write(out_line)

    os.rename(os.path.join(dst, 'famapy/metamodels/__NAME__'),
              os.path.join(dst, f'famapy/metamodels/{name}'))
    print("Done!")


def cmd_cli() -> None:
    subcommand = sys.argv[2:]
    if not subcommand:
        subcommand = ["help"]
    sys.argv = [".", "-m", "famapy.endpoint.diverso_lab", "cli", "-c"] + subcommand
    development_runner.hug.interface.cli()


def famapy_admin() -> None:
    main_parser = parser()

    options, _ = main_parser.parse_known_args()
    command = options.command

    if command is None:
        main_parser.print_help()
        sys.exit()

    if command == "new_plugin":
        cmd_new_plugin(options)

    if command == "cli":
        cmd_cli()
