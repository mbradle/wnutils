Reading in the Data
===================

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
`wnutils.read.xml`.  In python, you can import these routines by typing,
for example::

    >>> import wnutils.read.xml as wrx

Then use the `wrx` namespace in subsequent calls.

To illustrate the use of `wnutils.read.xml` routines, we use the files
`my_output1.xml` and `my_output2.xml`,
which you should have downloaded according to the
:ref:`data` tutorial.

Read zone properties as floats.
...............................

Type::

    >>> props = wrx.get_properties_in_zones_as_floats( 'my_output1.xml', ['time','t9','rho'] )
    >>> for i in range(len(props['time'])):
    ...     print(
    ...         'Zone = {0:d} time(s) = {1:.2e} t9 = {2:.2f} rho(g/cc) = {3:.2e}'.format(
    ...             i, props['time'][i], props['t9'][i], props['rho'][i]
    ...         )
    ...     )
    ...

This will output the time, temperature (in billions of K), and mass density
(in g/cc) in all zones (time steps).



HDF5
----

Routines that read these HDF5 files are in the namespace
`wnutils.read.h5`.  In python, you can import these routines by typing,
for example::

    >>> import wnutils.read.h5 as wr5

Then use the `wr5` namespace in subsequent calls.

Read the names of the iterable groups.
.......................................

Type::

     >>> groups = wr5.get_iterable_groups('my_output.h5')
     >>> for group in groups:
     ...     print(group)
     ...

Read properties of a zone in the groups.
........................................

Zones are retrieved by specifying the three labels as a tuple.  For example,
type::

     >>> zone = ('1','0','0')
     >>> props = wr5.get_zone_properties_in_groups('my_output.h5', zone, ['time','t9','rho'])
     >>> groups = wr5.get_iterable_groups('my_output.h5')
     >>> for in in range(len(groups)):
     ...     print(
     ...         '{0:s}: time(s) = {1:.2e} t9 = {2:.2f} rho(g/cc) = {3:.2e}'.format(
     ...             groups[i], props['time'][i], props['t9'][i], props['rho'][i]
     ...         )
     ...     )
     ...
