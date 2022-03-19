import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="famapy",
    version="0.7.1",
    author="Víctor Ramírez de la Corte",
    author_email="me@virako.es",
    description="FaMaPy is a Python-based AAFM framework that takes into consideration previous AAFM tool designs and enables multi-solver and multi-metamodel support for the integration of AAFM tooling on the Python ecosystem.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/FaMaPy/core",
    packages=setuptools.find_namespace_packages(include=['famapy.*']),
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
    scripts=[
        'scripts/famapy_admin.py',
        'scripts/famapy_cmd',
    ]
)
