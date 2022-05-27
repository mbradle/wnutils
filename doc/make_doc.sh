rm -f source/wnutils.*.rst
mkdir -p source/_static source/_templates
sphinx-apidoc -M -f -n -o source ../wnutils
make html
