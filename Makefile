.PHONY: build
build:
	rm -rf dist
	python3 setup.py sdist bdist_wheel

upload-testpypi:
	python3 -m twine upload --repository testpypi dist/*

upload-pypi:
	python3 -m twine upload --repository pypi dist/*

lint:
	prospector --zero-exit

mypy:
	mypy famapy

test:
	python -m pytest -sv

cov:
	coverage run --source=famapy -m pytest
	coverage report
	coverage html

start:
	hug -f famapy/endpoint/diverso-lab.py


start-cli:
	hug -f famapy/endpoint/diverso-lab.py -c
