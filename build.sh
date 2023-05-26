# Script to automate build for PyPI.

rm -fr dist
black wnutils/*.py
python -m pip install --upgrade build
python -m build
