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

..
    Command to generate my_output.xml:

    ./single_zone_network @tut.rsp

    with tut.rsp:
    --t9_0 10 --rho_0 1.e9 --tau 0.1 --tend 1 --steps 5
    --network_xml ../nucnet-tools-code/data_pub/my_net.xml
    --nuc_xpath "[z <= 30]"
    --init_mass_frac "{h1, 0.5}" --init_mass_frac "{n, 0.5}"
    --iterative_solver gmres --iterative_t9 2
    --output_xml my_output.xml

    Command to generate my_output.h5:

    ./multi_zone_network @multi.rsp  (compiled with exponential_t9_rho)

    with multi.rsp:
      --network_xml ../nucnet-tools-code/data_pub/my_net.xml
      --output_hdf5 my_output.h5
      --init_mass_frac "{he4, 0.96}" "{ne22, 0.035}" "{fe56, 0.005}"
      --tend 3.15e12
      --number_zones=32
      --mix_rate=1.e-7

    and code compiled with
      #include "network_data/multi_zone/detail/exponential_t9_rho.hpp"
 
