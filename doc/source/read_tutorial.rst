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
The class :obj:`wnutils.xml.Xml` has methods that read these XML files.
To begin, import the namespace by typing::

    >>> import wnutils.xml as wx

To illustrate the use of `wnutils.xml` routines, we use the files
`my_output1.xml` and `my_output2.xml`,
which you should have downloaded according to the
:ref:`data` tutorial.  For each file, create an Xml object.  For example,
type::

    >>> xml1 = wx.Xml('my_output1.xml')

Read zone properties as floats.
...............................

Type::

    >>> props = xml1.get_properties_as_floats( ['time','t9','rho'] )
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

Methods that read these HDF5 files are in the namespace
`wnutils.h5`.  The class that contains these methods is
:obj:`wnutils.h5.H5`.  Begin by importing the namespace by typing::

    >>> import wnutils.h5 as w5

Then create an object for your file `my_output.h5` by typing::

    >>> my_h5 = w5.H5('my_output.h5')

Read the names of the iterable groups.
.......................................

Type::

     >>> groups = my_h5.get_iterable_groups()
     >>> for group in groups:
     ...     print(group)
     ...

Read properties of a zone in the groups as floats.
..................................................

Zones are retrieved by specifying the three labels as a tuple.  For example,
type::

     >>> zone = ('1','0','0')
     >>> props = my_h5.get_zone_properties_in_groups_as_floats(zone, ['time','t9','rho'])
     >>> groups = my_h5.get_iterable_groups()
     >>> for in in range(len(groups)):
     ...     print(
     ...         '{0:s}: time(s) = {1:.2e} t9 = {2:.2f} rho(g/cc) = {3:.2e}'.format(
     ...             groups[i], props['time'][i], props['t9'][i], props['rho'][i]
     ...         )
     ...     )
     ...
