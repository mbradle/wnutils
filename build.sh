# Script to automate build for PyPI.

set -e

rm -fr dist
cd wnutils
black *.py
pylint --extension-pkg-whitelist=lxml.etree --disable=C0103,R0913,R0801 --fail-under=9.6 *.py
cd ..

# Run the fast, self-contained suite first, then the larger tutorial-data
# integration test.  The latter caches and verifies the OSF archive.
pytest -v tests --ignore=tests/integration
python tests/integration/run_osf_tests.py

python -m pip install --upgrade build
python -m build
python -m pip install --upgrade twine
echo ""
echo "All version numbers must be the same:"
echo ""

grep version wnutils/__about__.py | grep -v ","
grep version CITATION.cff | grep -v "cff-version"
grep Version doc/source/changelog.rst | grep -v Versioning | head -1
grep '^version = ' pyproject.toml

echo ""
echo "Check the release date:"
echo ""
grep date CITATION.cff
echo ""
