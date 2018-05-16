Read in the Data
================

`webnucleo <http://sourceforge.net/u/mbradle/blog/>`_ data files are
in either in `XML <https://www.w3.org/TR/REC-xml/>`_ or
`hdf5 <https://support.hdfgroup.org/HDF5/>`_ format.  `wnutils` routines
can read either format.  The namespace containing these routines is
`wnutils.read`.

XML
---

The format of `webnucleo` XML files is described in the libnucnet technical
report `XML Input to libnucnet`, available at the
`libnucnet Home page <https://sourceforge.net/p/libnucnet/home/Home/>`_.
Routines that read these XML files are in the namespace
`wnutils.read.xml`.

To illustrate the use of `wnutils.read.xml` routines, we use the file
`my_output.xml`, which you should have downloaded according to the
:ref:`data` tutorial.

HDF5
----

