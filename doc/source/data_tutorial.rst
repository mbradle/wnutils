.. _data:

Getting the Data
================

We have already generated some example data to use with these tutorials.
You must download those data from the web.

First, begin by creating a directory in which to work on the wnutils tutorials.
You might create this off your home directory, so you could type::

    $ cd ~
    $ mkdir wnutils_tutorials
    $ cd wnutils_tutorials

Next, make sure that you have `wget <https://www.gnu.org/software/wget/>`_
installed on your system by typing::

    $ wget --help

If this does not return a proper usage statement, you can probably install
it with these
`instructions <https://sourceforge.net/p/nucnet-projects/wiki/libraries/>`_.

Once you have ensured you have `wget`, download the tutorial data by typing::

    $ wget ...

This will download the tarball `wnutils_tutorials_data.tar.gz`.  Extract the
data by typing::

    $ gunzip wnutils_tutorials_data.tar.gz
    $ tar xvf wnutils_tutorials_data.tar.gz

You can now check that you have the expected files by typing::

    $ ls

You will see the files `my_output.h5`, `my_output.xml`, and
`wnutils_tutorials_data.tar`.  Since you have the data, you can remove
the tar file if you would like by typing::

    $ rm wnutils_tutorials_data.tar

You can always download that file again with `wget`.
