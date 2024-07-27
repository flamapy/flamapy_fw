import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()

def read_requirements(file):
    with open(file, "r") as fh:
        return fh.read().splitlines()

# Read development requirements from the dev-requirements.txt file
dev_requirements = read_requirements("requirements-dev.txt")

setuptools.setup(
    name="flamapy-fw",
    version="2.0.0.dev7",
    author="Flamapy",
    author_email="flamapy@us.es",
    description="Flamapy is a Python-based AAFM framework that takes into consideration previous AAFM tool designs and enables multi-solver and multi-metamodel support for the integration of AAFM tooling on the Python ecosystem.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/flamapy/core",
    packages=setuptools.find_namespace_packages(include=['flamapy.*']),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',
    extras_require={
        'dev': dev_requirements
    },
    entry_points={
        'console_scripts': [
            'flamapy = flamapy.commands:flamapy_cli',
        ],
    },
)
