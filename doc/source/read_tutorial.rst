.. _reading:

Reading in the Data
===================

`webnucleo <https://webnucleo.org/>`_ data files are
in either in `XML <https://www.w3.org/TR/REC-xml/>`_ or
`HDF5 <https://support.hdfgroup.org/HDF5/>`_ format.  `wnutils` routines
can read either format.

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

To illustrate the use of `wnutils.xml` routines, use the files
`my_output1.xml` and `my_output2.xml`,
which you should have downloaded according to the
:ref:`data` tutorial.  For each file, create an Xml object.  For example,
type::

    >>> my_xml = wx.Xml('my_output1.xml')

Read the nuclide data.
......................

You can retrieve the nuclide data in the webnucleo XML file by typing::

    >>> nuclides = my_xml.get_nuclide_data()

This returns a dictionary of data with the key being the nuclide name.
You may print out all the data for a specific nuclide, say, o16, by typing::

    >>> print(nuclides['o16'])

Or, to get specific data, try typing::

    >>> print('The mass excess in MeV of o16 is', nuclides['o16']['mass excess'])

It is possible to use an XPath expression to select out only certain
nuclides.  For example, to get the data for nitrogen isotopes only, type::

    >>> n = my_xml.get_nuclide_data(nuc_xpath='[z = 7]')

To confirm that you only retrieved nitrogen data, type::

    >>> for isotope in n:
    ...     print(isotope, ':', 'Z =', n[isotope]['z'], 'A =', n[isotope]['a'])
    ...

Partition function data for the nuclei
are stored in two :obj:`numpy.array` objects.  The first
array, with key `t9`, gives the temperature points (in billions of k) at which
the partition function is evaluated.  The second array, with key
`partf`, gives the partition function `G` evaluated at each of the
temperature points.
To see how this works, try printing out the partition function
for one of the iron isotopes, say, fe56.  Begin
by extracting the data for the iron isotopes by typing::

    >>> fe = my_xml.get_nuclide_data(nuc_xpath='[z = 26]')

Then print out the partition function `G` as a function of `t9` by typing::

    >>> sp = 'fe56'
    >>> for i in range(len(fe[sp]['t9'])):
    ...     print('t9 = ', fe[sp]['t9'][i], 'G(t9) = ', fe[sp]['partf'][i])
    ...

Read the network limits.
........................

It is often useful to know the limits of the network that comprises the
nuclei in the nuclear data collection.  To get this information, type::

    >>> lim = my_xml.get_network_limits()

This returns a :obj:`dict` of :obj:`numpy.array` objects.  The array
retrieved with key `z` gives the atomic numbers.  The array retrieved with
key `n_min` gives the smallest neutron number present for the corresponding
atomic number, while the array retrieved with key `n_max` gives the largest
neutron number present for the corresponding atomic number.  You can print
out the retrieved data by typing::

    >>> for z in range(len(lim['z'])):
    ...     print('Z =', z, ': N_min =', lim['n_min'][z], ', N_max =', lim['n_max'][z])
    ...

You can retrieve a subnetwork with an XPath expression.  For example,
you can type::

    >>> lim = my_xml.get_network_limits(nuc_xpath = '[z <= 5 or z >= 25]')

Now print out the data::

    >>> for i in range(len(lim['z'])):
    ...     print('Z =', lim['z'][i], ': N_min =', lim['n_min'][i], ', N_max =', lim['n_max'][i])
    ...

Read the reaction data.
.......................

You can retrieve the reaction data in the webnucleo XML file by typing::

    >>> reactions = my_xml.get_reaction_data()

This returns a dictionary with the key being the reaction string and each
value being a :class:`.Reaction`.  To see a list of the reactions, type::

    >>> for r in reactions:
    ...     print(r)
    ...

You can use an XPath expression to select the reactions.  For example, you
can type::

    >>> reactions = my_xml.get_reaction_data('[count(non_smoker_fit) = 1]')

Since the reaction data include the reaction type, you can confirm your request
by typing::

    >>> for r in reactions:
    ...    data = reactions[r].get_data()
    ...    print(r, ': type is', data['type'])
    ...

You may choose a particular reaction from the dictionary by typing, for
example::

    >>> reac = reactions['n + he4 + he4 -> be9 + gamma']

It is then possible to retrieve the `reactants`, `products`, the reaction
string, and code giving
the source by typing::

    >>> print(reac.reactants)
    >>> print(reac.products)
    >>> print(reac.get_string())
    >>> print(reac.source)

You can also compute the rate for the reaction (among interacting multiplets
and assuming one of the standard rate forms `single_rate`, `rate_table`,
or `non_smoker_fit`) at a variety of temperatures by typing::

    >>> import numpy as np
    >>> t9s = np.power(10., np.linspace(-2,1))
    >>> for t9 in t9s:
    ...     print(t9, reac.compute_rate(t9))
    ...

To compute the rate for user-defined rate functions, each defined with a
`user_rate` `key`, first write a python routine for each rate function,
then bind any data to that function (which must still take `t9` as an
argument), and then create a dictionary of the functions associated with
each `key`.  Pass that dictionary into the `compute_rate` method with
the keyword `user_funcs`.

Read all properties in a zone.
..............................

In a `webnucleo <http://webnucleo.org/>`_ XML file,
a `zone` is a collection of the `mutable` quantities during a network
calculation.  For a single-zone network calculation, a zone is often a
time step in the calculation.  The zone will contain mass fractions of
the network species at the time step to which the zone corresponds and
properties, which can be any quantity, such as time, temperature, or
density.  The properties themselves have a `name` and up to two `tags`,
called `tag1` and `tag2`.  If the property only has a name, it can
be retrieved by a :obj:`str`.  If the property has tags, the identifier
for the property is a :obj:`tuple` of up to three strings, namely,
the `name`, `tag1`, and `tag2`.

To retrieve all the properties of a given zone, say, the 10th zone,
type::

    >>> props = my_xml.get_all_properties_for_zone('[position() = 10]')

Now you can print out the properties and their values in this zone by
typing::

    >>> for prop in props:
    ...     print(str(prop).rjust(25), ':', props[prop])
    ...

Notice the conversion to :obj:`str` to print out the
`('exposure', 'n')` tuple correctly.

Read properties in all zones.
.............................

You can retrieve selected properties in all zones.  For the present example,
you retrieve the `time`, `t9` (temperature in billions of Kelvins),
and `rho` (mass density in g/cc) by typing::

    >>> props = my_xml.get_properties( ['time','t9','rho'] )

The properties are returned in the dictionary `props`.  Each dictionary
element is a list of strings giving the properties in the zones.
To see this, type::

    >>> print(props['time'])

This prints all the times.  Print the first time entry by typing::

    >>> print(props['time'][0])

To see the types, print::

    >>> type(props)

which shows that it is a hash (:obj:`dict`).  Next, type::

    >>> type(props['time'])

which shows that each dictionary entry is a :obj:`list`.  Next, type::

    >>> type(props['time'][0])

which shows each list entry is a :obj:`str`.

To retrieve properties with tags, you need to enter the appropriate
tuple.  For example, type::

    >>> props = my_xml.get_properties(['time', ('exposure', 'n')])

To print out the exposures, type::

    >>> for i in range(len(props[('exposure', 'n')])):
    ...     print('time:', props['time'][i], 'exposure:', props[('exposure', 'n')][i])
    ...

Read properties of selected zones.
..................................

You can select out the zones whose properties you wish to read by using
an `XPath <https://www.w3.org/TR/1999/REC-xpath-19991116/>`_ expression.
For example, you can retrieve the `time`, `t9`, and `rho` properties, as
in the above example, but only for the last 10 zones.  Type::

    >>> props = my_xml.get_properties(
    ...     ['time','t9','rho'], zone_xpath='[position() > last() - 10]'
    ... )

You can print the zone properties, for example, by typing::

    >>> print(props['t9'])

Confirm that there are only the properties for 10 zones by typing::

    >>> print(len(props['t9']))

Read zone properties as floats.
...............................

Properties are by default strings.  When you wish to manipulate them
(for example, to plot them), you want
them to be :obj:`float` objects.  You can retrieve them as floats by typing::

    >>> props = my_xml.get_properties_as_floats( ['time','t9','rho'] )

The returned hash has entries that are :obj:`numpy.array`, which you confirm
with::

    >>> type(props['rho'])

You can confirm that the array entries are floats by typing::

    >>> type(props['rho'][0])

You can print out the entries by typing::

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

You can retrieve the mass fractions in zones.  For example, to get the
mass fractions of o16, si28, and s36, type::

    >>> x = my_xml.get_mass_fractions(['o16','si28','s36']) 

The method returns a :obj:`dict` of :obj:`numpy.array`.  Each array element
is a :obj:`float`.  You can print the mass fraction of silicon-28 in all
zones by typing::

    >>> print(x['si28'])

The method also accepts the `zone_xpath` keyword to select specific zones.
For example, to retrieve the mass fraction in the first 10 zones, type::

    >>> x = my_xml.get_mass_fractions(
    ...      ['o16','si28','s36'], zone_xpath='[position() <= 10]'
    ... ) 

Read all abundances in zones.
.............................

You can retrieve abundances in the zones as a function of atomic and
neutron number.  The retrieved data are stored in a three-dimensional
:obj:`numpy.array`.  The first index gives the zone, the second
gives the atomic number, and the third gives the neutron number.  The
array value is the abundance (per nucleon).  Zones can be selected by
XPath.

To see how this works, retrieve the abundances in all zones by typing::

    >>> abunds = my_xml.get_all_abundances_in_zones()

Now print out the abundances in the 50th zone (remember the zero-indexing)
by typing::

    >>> for z in range(abunds.shape[1]):
    ...     for n in range(abunds.shape[2]):
    ...         print('Z =', z, ', N =', n, ', Y(Z,N) =', abunds[49,z,n])
    ...

You could do the same by typing::

    >>> abunds = my_xml.get_all_abundances_in_zones(zone_xpath='[position() = 50]')
    >>> for z in range(abunds.shape[1]):
    ...     for n in range(abunds.shape[2]):
    ...         print('Z =', z, ', N =', n, ', Y(Z,N) =', abunds[0,z,n])
    ...

This is because the XPath selects only one zone, which will have index 0 in
the retrieved data.

Retrieve abundances summed over nucleon number in zones.
........................................................

It is often convenient to retrieve the abundances of the nuclei in
a network file summed over proton number (`z`), neutron number (`n`),
or mass number (`a`).  To do so, type::

    >>> y = my_xml.get_abundances_vs_nucleon_number()

This returns a two-dimensional :obj:`numpy.array` in which the first
index gives the zone and the second the mass number `a`.  To print out
the abundances versus mass number in the eighth zone, type::

    >>> for i in range(y.shape[1]):
    ...     print('A:', i, 'Y(A):', y[7,i])
    ...

To retrieve
the abundances summed over atomic (proton) number (`z`), use the keyword
`nucleon`::

    >>> y = my_xml.get_abundances_vs_nucleon_number(nucleon='z')

To retrieve the abundances in particular zones, for example, in the
last 10 zones, use an XPath expression::

    >>> y = my_xml.get_abundances_vs_nucleon_number(nucleon='n', zone_xpath='[position() > last() - 10]')

Retrieve abundances for a chain of species.
...........................................

To retrieve the abundances for a set of isotopes or isotones, use the method
to get chain abundances.  For example, to retrieve the isotopic abundances for
`Z = 30` for all timesteps, type::

    >>> n, y = my_xml.get_chain_abundances(('z', 30))

The method returns a :obj:`tuple` with the first element being an array of
neutron numbers for the isotopes and the second element being a two dimensional
:obj:`numpy.array` with the abundances for each step.  To print the isotopic
abundances in the final step, type::

    >>> step = y.shape[0] - 1
    >>> for i in range(y.shape[1]):
    ...     print('N =', n[i], ', Y[N] =', y[step, i])
    ...

To return the isotonic abundances for `N = 25` in the first thirty timesteps,
type::

    >>> z, y = my_xml.get_chain_abundances(('n', 25), zone_xpath="[position() <= 30]")

To return the same isotonic abundances, but as a function of the mass number,
set the keyword variable `vs_A` to True::

    >>> a, y = my_xml.get_chain_abundances(('n', 25), zone_xpath="[position() <= 30]", vs_A=True)

To print these abundances in the thirtieth step, type::

    >>> step = y.shape[0] - 1
    >>> for i in range(y.shape[1]):
    ...     print('A =', a[i], ', Y[A] =', y[step, i])
    ...


Multi_XML
---------

The :obj:`wnutils.multi_xml.Multi_Xml` class allows you to access and plot data
from multiple webnucleo XML files.  First import the namespace by typing::

    >>> import wnutils.multi_xml as mx

Then create a class instance from a :obj:`list` of XML files.
For this tutorial, type

    >>> my_multi_xml = mx.Multi_Xml(['my_output1.xml','my_output2.xml'])

Methods allow you to access or plot data from the files.

Read data from the individual XML instances.
............................................

To retrieve the individual XML instances from a Multi_Xml instance, type::

    >>> xmls = my_multi_xml.get_xml()

To retrieve the original file names, type::

    >>> files = my_multi_xml.get_files()

Of course the number of XML instances must equal the number of files.  To
confirm, type::

    >>> print(len(xmls) == len(files))

Use the methods on the individual instances.  For example, type::

    >>> for i in range(len(xmls)):
    ...     props = xmls[i].get_properties(['time'])
    ...     print(files[i],'has',len(props['time']),'zones.')
    ...

H5
----

Methods that read webnucleo HDF5 files are in the namespace
`wnutils.h5`.  The class that contains these methods is
:obj:`wnutils.h5.H5`.  Begin by importing the namespace by typing::

    >>> import wnutils.h5 as w5

Then create an object for your file `my_output1.h5` (which you already
downloaded according to the instructions in the :ref:`data` tutorial)
by typing::

    >>> my_h5 = w5.H5('my_output1.h5')

Read the nuclide data.
......................

The nuclide data are in a group of their own in the file.  To retrieve the
data (as a :obj:`dict` of :obj:`dict` with the nuclide names as the top-level
dictionary keys), type::

    >>> nuclides = my_h5.get_nuclide_data()

Print out the data for, say, o16, by typing::

    >>> print(nuclides['o16'])

Print out the mass excess and spin for all species by typing::

    >>> for nuclide in nuclides:
    ...     print(nuclide, nuclides[nuclide]['mass excess'], nuclides[nuclide]['spin'])
    ...

Read the names of the iterable groups.
.......................................

Iterable groups are the groups in the HDF5 file that typically represent
timesteps (that is, the groups that are not the nuclide data group).
To retrieve their names (as a :obj:`list` of :obj:`str`), type::

     >>> groups = my_h5.get_iterable_groups()

Print them out by typing::

     >>> for group in groups:
     ...     print(group)
     ...

Read the zone labels for a group.
.................................

In a webnucleo HDF5 file, a zone is contained in a group and typically
represents a spatial region.  Zones are specified by three labels, which
we denote by a :obj:`tuple`.  To retrieve and print out the labels for a given
group, say, `Step 00010`, type::

    >>> labels = my_h5.get_zone_labels_for_group('Step 00010')
    >>> for i in range(len(labels)):
    ...     print('Zone',i,'has label',labels[i])
    ...

Read all properties in a zone for a group.
..........................................

To retrieve all the properties from a zone in a group, type, for example::

    >>> zone = ('2','0','0')
    >>> props = my_h5.get_group_zone_properties('Step 00010', zone)

You can print those properties out by typing::

    >>> for prop in props:
    ...     print(str(prop).rjust(25), ':', props[prop])
    ...

Read properties in all zones for a group.
.........................................

It is possible to retrieve the properties in all zones for a group as
as :obj:`dict` of :obj:`list`.  Each list entry is a :obj:`str`.  For example,
to retrieve and print the properties `time`, `t9`, and `rho` 
in all zones for a given group, say, `Step 00024`, type::

    >>> p = ['time','t9','rho']
    >>> props = my_h5.get_group_properties_in_zones('Step 00024',p)
    >>> labels = my_h5.get_zone_labels_for_group('Step 00024')
    >>> for i in range(len(labels)):
    ...     print('In',labels[i],'time=',props['time'][i],'t9=',props['t9'][i],'rho=',props['rho'][i])
    ...

Read properties in all zones for a group as floats.
...................................................

It is often desirable to retrieve the properties in zones for a group as floats.
For example,
one may again retrieve `time`, `t9`, and `rho` from `Step 00024` but,
this time, as floats by typing::

    >>> p = ['time','t9','rho']
    >>> props = my_h5.get_group_properties_in_zones_as_floats('Step 00024',p)
    >>> type(props['time'])
    >>> type(props['time'][0])

Read mass fractions in all zones for a group.
.............................................

You can read all the mass fractions in all the zones for a given group.  For
a group `Step 00021`, type::

    >>> x = my_h5.get_group_mass_fractions('Step 00021')

The array x is a 2d HDF5 :obj:`h5py:Dataset`.  The first index gives the zone
and the second the species.  To print out the mass fraction of ne20 in all
the zones, type::

    >>> i_ne20 = (my_h5.get_nuclide_data())['ne20']['index']
    >>> labels = my_h5.get_zone_labels_for_group('Step 00021')
    >>> for i in range(x.shape[0]):
    ...     print('Zone',labels[i],'has X(ne20) =',x[i,i_ne20])
    ...

Read properties of a zone in the groups.
........................................

It is possible to retrieve properties from a given zone in all groups.
To retrieve the properties `time`, `t9`, and
`rho` in all groups for the zone with labels `1`, `0`, `0`, type::

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

One often wants the properties of a zone in the groups as floats.
To retrieve the properties `time`, `t9`, and
`rho` in all group for the zone with labels `1`, `0`, `0`, type::

     >>> zone = ('1','0','0')
     >>> props = my_h5.get_zone_properties_in_groups_as_floats(zone, ['time','t9','rho'])

This returns a :obj:`dict` of :obj:`numpy.array`.  Each array entry is a
:obj:`float`.  To print the properties out in the groups, type::

     >>> groups = my_h5.get_iterable_groups()
     >>> for i in range(len(groups)):
     ...     print(
     ...         '{0:s}: time(s) = {1:.2e} t9 = {2:.2f} rho(g/cc) = {3:.2e}'.format(
     ...             groups[i], props['time'][i], props['t9'][i], props['rho'][i]
     ...         )
     ...     )
     ...

Read mass fractions in a zone in the groups.
............................................

You can retrieve the mass fractions of specific species for a given zone in all
the iterable groups.  For example, to retrieve `o16`, `o17`, and `o18` in the
zone with labels `1`, `0`, `0`, type::

    >>> species = ['o16','o17','o18']
    >>> zone = ('1','0','0')
    >>> x = my_h5.get_zone_mass_fractions_in_groups( zone, species )

To print them out, you can now type::

    >>> groups = my_h5.get_iterable_groups()
    >>> for i in range(len(groups)):
    ...     print(groups[i],':','X(o16)=',x['o16'][i],'X(o17)=',x['o17'][i],'X(o18)=',x['o18'][i])
    ... 

Multi_H5
--------

The :obj:`wnutils.multi_h5.Multi_H5` class allows you to access and plot data
from multiple webnucleo HDF5 files.  First import the namespace by typing::

    >>> import wnutils.multi_h5 as m5

Then create a class instance from a :obj:`list` of HDF5 files.
For this tutorial, type

    >>> my_multi_h5 = m5.Multi_H5(['my_output1.h5','my_output2.h5'])

Methods allow you to access or plot data from the files.

Read data from the individual HDF5 instances.
.............................................

To retrieve the individual HDF5 instances from a Multi_H5 instance, type::

    >>> h5s = my_multi_h5.get_h5()

To retrieve the original file names, type::

    >>> files = my_multi_h5.get_files()

Of course the number of HDF5 instances must equal the number of files.  To
confirm, type::

    >>> print(len(h5s) == len(files))

Use the methods on the individual instances.  For example, type::

    >>> for i in range(len(h5s)):
    ...     props = h5s[i].get_zone_properties_in_groups(('0','0','0'), ['time'])
    ...     print(files[i],'has',len(props['time']),'groups.')
    ...

