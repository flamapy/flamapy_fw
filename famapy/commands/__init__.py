#!/usr/bin/python

import argparse
import os
import sys
from shutil import copytree

import hug


def famapy_admin():
    # Parser arguments
    main_parser = argparse.ArgumentParser()
    subparser = main_parser.add_subparsers(title="commands", dest="command")

    new_plugin = subparser.add_parser("new_plugin", help="new_plugin")
    new_plugin.add_argument('name', type=str, help='A name for your plugin. Ex: fama')
    new_plugin.add_argument('extension', type=str, help='A extension for your plugin. Ex: fm')
    new_plugin.add_argument('--path', default='.', type=str, help='Plugin project path.  Default: .')

    subparser.add_parser("cli", help="cli", description='famapy_admin.py api: command line api')

    options, args = main_parser.parse_known_args()
    command = options.command


    if command is None:
        main_parser.print_help()
        exit()


    if command == "new_plugin":
        NAME = options.name
        EXT = options.extension
        DST = options.path
        SRC = 'skel_metamodel/'

        # Check DST exist
        if not os.path.isdir(DST):
            print(f"Folder {DST} not exist")
            sys.exit()

        # Check DST is empty
        if len(os.listdir(DST)) != 0:
            print(f"Folder {DST} is not empty")
            sys.exit()

        # Check DST has permissions to WRITE
        if not os.access(DST, os.W_OK):
            print(f"Folder {DST} has not write permissions")
            sys.exit()

        # Generating structure
        print("Generating structure ...")

        copy_files = copytree(SRC, DST)

        for copy_file in copy_files:
            with open(copy_file, "r") as f:
                lines = f.readlines()
            with open(copy_file, "w") as fw:
                for line in lines:
                    out_line = line.replace('__NAME__', NAME.capitalize()).replace('__EXT__', EXT)
                    fw.write(out_line)

        os.rename(os.path.join(DST, 'famapy/metamodels/__NAME__'),
                  os.path.join(DST, f'famapy/metamodels/{NAME}'))
        print("Done!")

    if command == "cli":
        subcommand = sys.argv[2:]
        if not subcommand:
            subcommand = ["help"]
        sys.argv = [".", "-m", "famapy.endpoint.diverso_lab", "cli", "-c"] + subcommand
        hug.development_runner.hug.interface.cli()
