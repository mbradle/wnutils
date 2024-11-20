# Script to automate build for PyPI.

rm -fr dist
cd wnutils
git clone https://bitbucket.org/mbradle/libnucnet_xsd.git xsd_pub 2> /dev/null || git -C xsd_pub pull
black --line-length=79 *.py
cd ..
python -m pip install --upgrade build
python -m build
