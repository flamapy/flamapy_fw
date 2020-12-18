.PHONY: build
build:
	rm -rf dist
	python3 setup.py sdist bdist_wheel

upload-testpypi:
	python3 -m twine upload --repository testpypi dist/*

upload-pypi:
	python3 -m twine upload --repository pypi dist/*

test:
	python -m pytest

interantive-test:
	python -m pytest -s


start:
	hug -f famapy/endpoint/diverso-lab.py


start-cli:
	hug -f famapy/endpoint/diverso-lab.py -c
