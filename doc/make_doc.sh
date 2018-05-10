rm source/modules.rst
rm source/wnutils.rst
rm source/wnutils.plot.rst
rm source/wnutils.read.rst
sphinx-apidoc -M -f -o source ../wnutils
make html
