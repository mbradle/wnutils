Reading in the Data
===================

`webnucleo <http://sourceforge.net/u/mbradle/blog/>`_ data files are
in either in `XML <https://www.w3.org/TR/REC-xml/>`_ or
`hdf5 <https://support.hdfgroup.org/HDF5/>`_ format.  `wnutils` routines
can read either format.  The namespace containing these routines is
`wnutils.read`.

In the following tutorials, you will enter Python commands.  In your
terminal, type python (or python3, or, perhaps, python2.x or python3.x,
depending on your version).  You will see something like::

    Python 3.6.5 (default, Mar 29 2018, 15:38:28) 
    [GCC 4.2.1 Compatible Apple LLVM 7.3.0 (clang-703.0.31)] on darwin
    Type "help", "copyright", "credits" or "license" for more information.
    >>>

The >>> is the interactive python prompt (it will typically show up in the
tutorials in red).  You type your commands at this
prompt.  To exit python, type::

    >>> exit()

and hit enter.

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

    >>> my_xml_1 = wx.Xml('my_output1.xml')

Read zone properties.
.....................

We can retrieve properties in zones.  For our example, we retrieve the
`time`, `t9` (temperature in billions of Kelvins), and `rho` (mass density
in g/cc) by typing::

    >>> props = my_xml_1.get_properties( ['time','t9','rho'] )

The properties are returned in the hash `props`.  Each hash element is
a list of strings giving the properties in the zones.  To see this, type::

    >>> print(props['time'])

This prints all the times.  Print the first time entry by typing::

    >>> print(props['time'][0])

To see the types, print::

    >>> type(props)

which shows that it is a hash (:obj:`dict`).  Next, type::

    >>> type(props['time'])

which shows that each dictionary entry is a :obj:`list`.  Next, type::

    >>> print(props['time'][0])

which shows each list entry is a :obj:`str`.

Read properties of selected zones.
..................................

We can select out the zones whose properties we wish to read by using
an `XPath <https://www.w3.org/TR/1999/REC-xpath-19991116/>`_ expression.
For example, we can retrieve the `time`, `t9`, and `rho` properties, as
in the above example, but only for the last 10 zones.  We type::

    >>> props = my_xml_1.get_properties(
    ...     ['time','t9','rho'], zone_xpath='[position() > last() - 10]'
    ... )
    ...

We print the zone properties, for example, by typing::

    >>> print(props['t9'])

We confirm that we only have the properties for 10 zones by typing::

    >>> print(len(props['t9'])

Read zone properties as floats.
...............................

Properties are by default strings.  When we wish to manipulate them
(for example, to plot them), we want
them to be :obj:`floats`.  We can retrieve them as floats by typing::

    >>> props = my_xml_1.get_properties_as_floats( ['time','t9','rho'] )

The returned hash has entries that are :obj:`numpy.array`, which we confirm
with::

    >>> type(props['rho'])

We can confirm that the array entries are floats by typing::

    >>> type(props['rho'][0])

We can print out the entries by typing::

    >>> for i in range(len(props['time'])):
    ...     print(
    ...         'Zone = {0:d} time(s) = {1:.2e} t9 = {2:.2f} rho(g/cc) = {3:.2e}'.format(
    ...             i, props['time'][i], props['t9'][i], props['rho'][i]
    ...         )
    ...     )
    ...

This will output the time, temperature (in billions of K), and mass density
(in g/cc) in all zones (time steps).

Read mass fractions in zones.
.............................

We can retrieve the mass fractions in zones.  For example, to get the
mass fractions of o16, si28, and s36, we type::

    >>> x = my_xml_1.get_mass_fractions(['o16','si28','s36']) 

The method returns a :obj:`dict` of :obj:`numpy.array`.  Each array element
is a :obj:`float`.  We can print the mass fraction of silicon-28 in all
zones by typing::

    >>> print(x['si28'])

The method also accepts the `zone_xpath` keyword to select specific zones.
For example, to retrieve the mass fraction in the first 10 zones, type::

    >>> x = my_xml_1.get_mass_fractions(
    ...      ['o16','si28','s36'], zone_xpath='[position() <= 10]'
    ... ) 
    ...

Retrieve abundances summed over nucleon number in zones.
........................................................

It is often convenient to retrieve the abundances of the nuclei in
a network file summed over proton number (`z`), neutron number (`n`),
or mass number (`a`).  To do so, we can type::

    >>> y = my_xml_1.get_abundances_vs_nucleon_number()

This returns a two-dimensional :obj:`numpy.array` in which the first
index gives the zone and the second the mass number `a`.  To print out
the abundances versus mass number in the eighth zone, type::

    >>> for i in range(y.shape[1]):
    ...     print('A:', i, 'Y(A):', y[7,i])
    ...

To retrieve
the abundances summed over atomic (proton) number (`z`), use the keyword
`nucleon`::

    >>> y = my_xml_1.get_abundances_vs_nucleon_number(nucleon='z')

To retrieve the abundances in particular zones, for example, in the
last 10 zones, use an XPath expression::

    >>> y = my_xml_1.get_abundances_vs_nucleon_number(nucleon='n', zone_xpath='[position() > last() - 10]')



HDF5
----

Methods that read webnucleo HDF5 files are in the namespace
`wnutils.h5`.  The class that contains these methods is
:obj:`wnutils.h5.H5`.  Begin by importing the namespace by typing::

    >>> import wnutils.h5 as w5

Then create an object for your file `my_output.h5` (which you already
downloaded) by typing::

    >>> my_h5 = w5.H5('my_output.h5')

Read the names of the iterable groups.
.......................................

Iterable groups are the groups in the HDF5 file that typically represent
timesteps.  To retrieve their names (as a :obj:`list` of :obj:`str`), type::

     >>> groups = my_h5.get_iterable_groups()

Print them out by typing::

     >>> for group in groups:
     ...     print(group)
     ...

Read properties of a zone in the groups.
........................................

In a webnucleo HDF5 file, a zone is contained in a group and typically
represents a spatial region.  Zones are specified by three labels, which
we denote by a :obj:`tuple`.  To retrieve the properties `time`, `t9`, and
`rho` in all group for the zone with labels `1`, `0`, `0`, type::

     >>> zone = ('1','0','0')
     >>> props = my_h5.get_zone_properties_in_groups(zone, ['time','t9','rho'])

This returns a :obj:`dict` of :obj:`list` of :obj:`str`.
To print the properties out in the groups, type::

     >>> groups = my_h5.get_iterable_groups()
     >>> for i in range(len(groups)):
     ...     print(
     ...         groups[i], ': ', props['time'][i], props['t9'][i], props['rho'][i]
     ...     )
     ...

Read properties of a zone in the groups as floats.
..................................................

In a webnucleo HDF5 file, a zone is contained in a group and typically
represents a spatial region.  Zones are specified by three labels, which
we denote by a :obj:`tuple`.  To retrieve the properties `time`, `t9`, and
`rho` in all group for the zone with labels `1`, `0`, `0`, type::

     >>> zone = ('1','0','0')
     >>> props = my_h5.get_zone_properties_in_groups_as_floats(zone, ['time','t9','rho'])

This returns a :obj:`dict` of :obj:`numpy.array`.  Each array entry is a
float.  To print the properties out in the groups, type::

     >>> groups = my_h5.get_iterable_groups()
     >>> for i in range(len(groups)):
     ...     print(
     ...         '{0:s}: time(s) = {1:.2e} t9 = {2:.2f} rho(g/cc) = {3:.2e}'.format(
     ...             groups[i], props['time'][i], props['t9'][i], props['rho'][i]
     ...         )
     ...     )
     ...
