#!/usr/bin/python

import argparse


# TODO: add option to add operation


# Parser arguments
parser = argparse.ArgumentParser(description='famapy-script.py: generate structure for new plugins')
parser.add_argument('name', type=str, help='A name for your plugin. Ex: fama')
parser.add_argument('extension', type=str, help='A extension for your plugin. Ex: fm')
parser.add_argument('--path', default='.', type=str, help='Plugin project path.  Default: .')
args = parser.parse_args()

NAME = args.name
EXT = args.extension
PATH = args.path

# Generating structure
print("Generating structure ...")



# TODO LIST
# 1. get arguments (name and path)
# 2. check name and path is valid (permissions and empty folder)
# 3. copy skel_metamodel to path and change the name by name
# 4. change folders with __metamodel__ name and change files with __Metamodel__

print("Done!")
