import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="flamapy",
    version="1.0.1",
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
    install_requires=[
        'hug>=2.6.1',
    ],
    extras_require={
        'dev': [
            'pytest',
            'pytest-mock',
            'prospector',
            'mypy',
            'coverage',
        ]
    },
    entry_points={
        'console_scripts': [
            'flamapy-admin = flamapy.commands:flamapy_admin',
        ],
    },
)
