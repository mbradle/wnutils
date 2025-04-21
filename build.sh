# Script to automate build for PyPI.

rm -fr dist
cd wnutils
git clone https://bitbucket.org/mbradle/libnucnet_xsd.git xsd_pub 2> /dev/null || git -C xsd_pub pull
black --line-length=79 *.py
pylint --extension-pkg-whitelist=lxml.etree --disable=C0103,R0913,R0801 --fail-under=9.6 *.py
cd ../.github/workflows/
pytest
cd ../..

python -m pip install --upgrade build
python -m build
python -m pip install --upgrade twine
echo ""
echo "All version numbers must be the same:"
echo ""

grep version wnutils/__about__.py | grep -v ","
grep version CITATION.cff | grep -v "cff-version"
grep Version doc/source/changelog.rst | grep -v Versioning | head -1
grep version pyproject.toml

echo ""
echo "Check the release date:"
echo ""
grep date CITATION.cff
echo ""
