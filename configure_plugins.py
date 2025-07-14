import os
import sys

import setuptools


def env_list(env_variable: str, default: list[str]) -> list[str]:
    result: str = os.environ.get(env_variable)

    if not result:
        return default

    return result.split(":")


# Get plugins folder by environment variable

PLUGIN_PATHS: list[str] = env_list("PLUGIN_PATHS", [])

if not PLUGIN_PATHS:
    print("You can configure your plugins with an environment variable: Example:")
    print("export PLUGIN_PATHS=/home/foo/plugin1:/home/foo/plugin2")
    want_continue = input("No plugins selected. Do you want to continue? (y/n)")

    if not want_continue.lower().startswith("y"):
        print("See you soon :)")
        sys.exit(0)


# Create symbolic link

CORE_PLUGIN_DIRECTORY = "flamapy/metamodels/"
if not os.path.exists(CORE_PLUGIN_DIRECTORY):
    os.mkdir(CORE_PLUGIN_DIRECTORY)


for plugin_path in PLUGIN_PATHS:
    if not os.path.exists(plugin_path):
        print(f"{plugin_path} path not found")
        continue

    plugin_directories = setuptools.find_namespace_packages(
        plugin_path, include=["flamapy.metamodels.*"], exclude=["flamapy.metamodels.*.*"]
    )

    for plugin_directory in plugin_directories:
        src = os.path.join(plugin_path, plugin_directory.replace(".", "/"))
        dst = os.path.join(CORE_PLUGIN_DIRECTORY, plugin_directory.split(".")[-1])
        if os.path.exists(src) and not os.path.exists(dst):
            os.symlink(src, dst)
