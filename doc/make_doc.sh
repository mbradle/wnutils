rm -f source/modules.rst source/wnutils.*.rst
mkdir -p source/_static source/_templates
sphinx-apidoc -M -f -o source ../wnutils
make html
