.. _writing:

Creating and Writing XML Data
=============================

The preferred format for `webnucleo <http://webnucleo.org/>`_
data input is `XML <https://www.w3.org/TR/REC-xml/>`_.
`wnutils` routines allow users to create or update such XML.

The format of `webnucleo` XML files is described in the libnucnet technical
report `XML Input to libnucnet`, available at the
`libnucnet Home page <https://sourceforge.net/p/libnucnet/home/Home/>`_.
The class :obj:`wnutils.xml.New_Xml` has methods that create new XML, set
the nuclide, reaction, or zone data in the XML, and write the XML to a file.
To begin, import the namespace by typing::

    >>> import wnutils.xml as wx

Nuclide XML Data
----------------

Extract a subset of nuclide data.
.................................

Begin by retrieving the data that you wish to update.
For this tutorial, use the file `my_output1.xml` which you should have
downloaded according to the :ref:`data` tutorial.  Read in the data by
typing

    >>> old_xml = wx.Xml('my_output1.xml')

Now get a subset of the nuclide data using an XPath expression.  For this
tutorial, get a subset that excludes calcium isotopes or any species with
mass number 30 by typing

    >>> nuclide_subset = old_xml.get_nuclide_data("[not(z = 20) and not(a = 30)]")

Confirm that the subset does not have the excluded species by examining the
result of typing

    >>> for nuc in nuclide_subset:
    ...     print(nuclide_subset[nuc]['z'], nuclide_subset[nuc]['a'])
    ...

Now create new nuclear data XML by typing

    >>> subset_xml = wx.New_Xml(xml_type='nuclear_data')

Set the data in the new XML by typing

    >>> subset_xml.set_nuclide_data(nuclide_subset)

and write the data to an XML file by typing

    >>> subset_xml.write('subset_nuclear_data.xml')

You can now read those data into an Xml object by typing

    >>> xml = wx.Xml('subset_nuclear_data.xml')

Now compare the two data files.  Get the calcium and A=30 isotopes from
both files and print out by typing

    >>> check_old = old_xml.get_nuclide_data("[(z = 20) or (a = 30)]")
    >>> print(len(check_old))
    >>> check_new = xml.get_nuclide_data("[(z = 20) or (a = 30)]")
    >>> print(len(check_new))

The old XML file contains calcium and A=30 isotopes but the new XML file
does not.
    
Update existing nuclide data.
.............................

To update existing data, retrieve the nuclide data by typing

    >>> nuclides = old_xml.get_nuclide_data()

`nuclides` is a dictionary with an entry for each nuclide chosen by the
XPath expression input to the `get_nuclide_data()` method.  The above
routine call retrieves all the nuclide data.  Each dictionary entry is itself
a dictionary.  To see the contents of an entry, type

    >>> print(nuclides['o16'])

This shows that the dictionary entries for o16. Update the data for this species
by typing

    >>> nuclides['o16']['source'] = 'made-up data'
    >>> nuclides['o16']['mass excess'] = 100
    >>> nuclides['o16']['t9'] = [1,2,3,4]
    >>> nuclides['o16']['partf'] = [1, 4, 9, 16]

Confirm the changes by typing

    >>> print(nuclides['o16'])

Now create a new nuclear data XML file by typing

    >>> updated_xml = wx.New_Xml(xml_type='nuclear_data')

Set the data in the new XML by typing

    >>> updated_xml.set_nuclide_data(nuclides)

and write the data to an XML file by typing

    >>> updated_xml.write('updated_nuclear_data.xml')

You can now read those data into an Xml object by typing

    >>> xml = wx.Xml('updated_nuclear_data.xml')

Validate those data against the libnucnet XML nuclear data schema by typing

    >>> xml.validate()

This will simply return, which shows that the data are valid.  Next, retrieve
the nuclide data and print out the o16 data:

    >>> updated_nuclides = xml.get_nuclide_data()
    >>> print(updated_nuclides['o16'])

The data in the new file are those that you have updated.

Add to existing nuclide data.
.............................

To add to existing data, retrieve the nuclide data by typing

    >>> nuclides = old_xml.get_nuclide_data()

Create a new species in the nuclide data by typing

    >>> nuclides['new'] = {}

Notice that the key can be any string different from the existing keys.  Now
add the data:

    >>> nuclides['new']['z'] = 122
    >>> nuclides['new']['a'] = 330
    >>> nuclides['new']['source'] = 'made-up'
    >>> nuclides['new']['state'] = ''
    >>> nuclides['new']['mass excess'] = 500
    >>> nuclides['new']['spin'] = 0.
    >>> nuclides['new']['t9'] = [1,2,3,4]
    >>> nuclides['new']['partf'] = [1,4,9,16]

Create the new XML, set the data, and write out the XML:

    >>> extended_xml = wx.New_Xml(xml_type='nuclear_data')
    >>> extended_xml.set_nuclide_data(nuclides)
    >>> extended_xml.write('extended_nuclear_data.xml')

Read in the extended XML, validate, and print out the nuclide data to confirm
the new species has been added:

    >>> xml = wx.Xml('extended_nuclear_data.xml')
    >>> xml.validate()
    >>> extended_nuclides = xml.get_nuclide_data()
    >>> for nuc in extended_nuclides:
    ...     print(nuc, extended_nuclides[nuc]['z'], extended_nuclides[nuc]['a'])
    ...

Create new nuclide data.
........................

To create new nuclide XML data, first create a nuclide data dictionary:

    >>> nuclides = {}

Now add species:

    >>> t9 = [1,2,3,4]
    >>> partf = [1,4,9,16]
    >>> nuclides['new1'] = {'z': 13, 'a': 26, 'state': 'g', 'source': 'wn_tutorial', 'mass excess': -12.2101, 'spin': 5, 't9': t9, 'partf': partf}
    >>> t9 = [1,2,3,4]
    >>> partf = [1,8,27,64]
    >>> nuclides['new2'] = {'z': 13, 'a': 26, 'state': 'm', 'source': 'wn_tutorial', 'mass excess': -11.9818, 'spin': 0, 't9': t9, 'partf': partf}

Create the new XML, set the data, write out the XML, read in the XML,
and print out the nuclide data::

    >>> new_xml = wx.New_Xml(xml_type='nuclear_data')
    >>> new_xml.set_nuclide_data(nuclides)
    >>> new_xml.write('new_nuclear_data.xml')
    >>> xml = wx.Xml('new_nuclear_data.xml')
    >>> new_nuclides = xml.get_nuclide_data()
    >>> for nuc in new_nuclides:
    ...     print(nuc, new_nuclides[nuc]['z'], new_nuclides[nuc]['a'])
    ...

This shows the two species in the new XML file.

Reaction XML Data
-----------------

Create new reaction XML analogously to creating new nuclide XML.
Update an existing reaction data dictionary or create a new one, create
a new reaction XML object, set the data in the object, and write to XML.

Extract a subset of reaction data.
..................................

To extract a subset of reaction data, first retrieve the data and get
the data subset with XPath by typing

    >>> old_xml = wx.Xml('my_output1.xml')
    >>> reactions = old_xml.get_reaction_data("[not(reactant = 'kr85') and not(product = 'kr85')]")

The reactions data includes all reactions in the old data set except those
involving *kr85*.  Now create and write to XML:

    >>> subset_xml = wx.New_Xml(xml_type='reaction_data')
    >>> subset_xml.set_reaction_data(reactions)
    >>> subset_xml.write('subset_reaction_data.xml')

One can now read in the data and validate:

    >>> xml = wx.Xml('subset_reaction_data.xml')
    >>> xml.validate()

Now check that the *kr85* reactions have been excluded:

    >>> old_kr85 = old_xml.get_reaction_data("[reactant = 'kr85' or product = 'kr85']")
    >>> new_kr85 = xml.get_reaction_data("[reactant = 'kr85' or product = 'kr85']")
    >>> for reaction in old_kr85:
    ...     print(reaction)
    ...
    >>> for reaction in new_kr85:
    ...     print(reaction)
    ...

The old XML data file includes reactions involving *kr85* but the new one
does not.

Update existing reaction data.
..............................

To update existing data, retrieve the reaction data by typing

    >>> reactions = old_xml.get_reaction_data()

*reactions* is a dictionary with an entry for each reaction chosen by
the input XPath expression.  The above call selects all reactions.  Each
entry in the dictionary is itself an instance of the
:obj:`wnutils.xml.Reaction` class containing data for the
reaction.  To see an example of the data, type

    >>> print(reactions['n + f19 -> f20 + gamma'].reactants)
    >>> print(reactions['n + f19 -> f20 + gamma'].products)
    >>> print(reactions['n + f19 -> f20 + gamma'].source)
    >>> print(reactions['n + f19 -> f20 + gamma'].get_data())

The last command shows that the rate data for the reaction are of the
*non_smoker_fit* type and are contained
in a dictionary.  Now update the data.  Type

    >>> reactions['n + f19 -> f20 + gamma'].source = 'ka02--updated'
    >>> reactions['n + f19 -> f20 + gamma'].get_data()['fits'][0]['spint'] = 99.

It is also possible to change the data type.
Change the *n + f20 -> f21 + gamma* from *non_smoker_fit* type to a
*rate_table* type:

    >>> print(reactions['n + f20 -> f21 + gamma'].get_data())
    >>> t9 = [0.1,1,2,10]
    >>> rate = [200, 150, 125, 100]
    >>> sef = [1,1,1,1]
    >>> reactions['n + f20 -> f21 + gamma'].data = {'type': 'rate_table', 't9': t9, 'rate': rate, 'sef': sef}

The *t9* array gives the temperatures (in billions of K) at which the
rates (*rate* array) are given.  The *sef* is the *stellar enhancement
factor*, which is the factor by which ground-state rate is increased in
a stellar environment.  When no *sef* is given, set it to unity.

Now confirm that the data have been updated by typing

    >>> print(reactions['n + f19 -> f20 + gamma'].source)
    >>> print(reactions['n + f19 -> f20 + gamma'].get_data())
    >>> print(reactions['n + f20 -> f21 + gamma'].data)

Notice that the last command simply directly accessed the
Reaction class member *data* instead of using the *get_data()* method.
Either is valid--the *get_data()* method
is simply a legacy convenience method
that returns the class member *data*.  Confirm the actions are the
same by typing

    >>> print(reactions['n + f20 -> f21 + gamma'].get_data())

Now create new XML and write the updated data:

    >>> updated_xml = wx.New_Xml(xml_type='reaction_data')
    >>> updated_xml.set_reaction_data(reactions)
    >>> updated_xml.write('updated_reaction_data.xml')

Now confirm that the updated XML has the changes:

    >>> xml = wx.Xml('updated_reaction_data.xml')
    >>> updated_reactions = xml.get_reaction_data()
    >>> print(updated_reactions['n + f19 -> f20 + gamma'].source)
    >>> print(updated_reactions['n + f19 -> f20 + gamma'].get_data())
    >>> print(updated_reactions['n + f20 -> f21 + gamma'].get_data())


Add to existing reaction data.
..............................

It is possible to add to existing reaction data.  To try this,
create the reaction *ni70 -> cu65 + n + n + n + n + n + electron +
anti-neutrino_e* with a single rate of 1.5 per second:

    >>> r = wx.Reaction()
    >>> r.reactants = ['ni70']
    >>> r.products = ['cu65', 'n', 'n', 'n', 'n', 'n', 'electron', 'anti-neutrino_e']
    >>> r.source = 'wn_tutorials'
    >>> r.data = {'type': 'single_rate', 'rate': 1.5}

Now add this to the existing data:

    >>> old_xml = wx.Xml('my_output1.xml')
    >>> reactions = old_xml.get_reaction_data()
    >>> reactions['new'] = r

Create and write new XML with the extended data:

    >>> extended_xml = wx.New_Xml(xml_type='reaction_data')
    >>> extended_xml.set_reaction_data(reactions)
    >>> extended_xml.write('extended_reaction_data.xml')

Confirm that the new XML has the added data:

    >>> xml = wx.Xml('extended_reaction_data.xml')
    >>> extended_reactions = xml.get_reaction_data("[reactant = 'ni70']")
    >>> for reaction in extended_reactions:
    ...     print(reaction)
    ...
    >>> print(extended_reactions['ni70 -> cu65 + n + n + n + n + n + electron + anti-neutrino_e'].get_data())


Create new reaction data.
.........................

It is also possible to create new reaction XML data.  One creates a
new reaction data dictionary and then sets those data in new XML and
writes the XML out.  To experiment with this, create a new reaction
XML file with a *non_smoker_fit* data set and two *user_rate* data sets.
In *user_rate* data, each rate datum is a *property* that is denoted
by a :obj:`str` giving the property *name* or a :obj:`tuple` giving the
property *name* and up to two tags (*tag1* and *tag2*).  First, create
the reactions data and add the *non_smoker_fit* reaction:

    >>> reactions = {}
    >>> reactions['new1'] = wx.Reaction()
    >>> reactions['new1'].reactants = ['ge111', 'h1']
    >>> reactions['new1'].products = ['as112', 'gamma']
    >>> reactions['new1'].source = 'ADNDT (2001) 75, 1 (non-smoker)'
    >>> reactions['new1'].data = {'type': 'non_smoker_fit', 'fits': [{'spint': 0.5, 'spinf': 1.0, 'TlowHf': -1.0, 'Tlowfit': 0.01, 'Thighfit': 10.0, 'acc': 0.035, 'a1': 204.211, 'a2': -10.533, 'a3': 414.2, 'a4': -658.043, 'a5': 37.4352, 'a6': -2.17474, 'a7': 326.601, 'a8': 227.497}]}

Now add the first *user_rate* data reaction:

    >>> reactions['new2'] = wx.Reaction()
    >>> reactions['new2'].reactants = ['c12', 'c12']
    >>> reactions['new2'].products = ['mg23', 'n']
    >>> reactions['new2'].source = 'CF88'
    >>> reactions['new2'].data = {'type': 'user_rate', 'key': 'cf88 carbon fusion fit',
    ...                           'f_0.11_le_t9_lt_1.75': '0.0', 'f_1.75_le_t9_lt_3.3': '0.05',
    ...                           'f_3.3_le_t9_lt_6': '0.07', 'f_t9_ge_6': '0.07', 'f_t9_lt_0.11': '0.0'}

Notice that all properties in the data dictionary are of :obj:`str` type.
Also note that the *user_rate* needs a *key* entry denoting the particular
user-rate function that will be used to compute the rate from the data.  Now
add the second *user_rate* data reaction:

    >>> reactions['new3'] = wx.Reaction()
    >>> reactions['new3'].reactants = ['c12', 'he4']
    >>> reactions['new3'].products = ['o16', 'gamma']
    >>> reactions['new3'].source = 'Kunz et al. (2002)'
    >>> reactions['new3'].data = {'type': 'user_rate', 'key': 'kunz fit', ('a', '0'): ' 1.21e8',
    ...                           ('a', '1'): ' 6.06e-2', ('a', '10'): ' 2.e6', ('a', '11'): ' 38.534',
    ...                           ('a', '2'): ' 32.12', ('a', '3'): ' 1.7', ('a', '4'): ' 7.4e8',
    ...                           ('a', '5'): ' 0.47', ('a', '6'): ' 32.12', ('a', '7'): ' 0.',
    ...                           ('a', '8'): ' 0.', ('a', '9'): ' 1.53e4'}

Notice here that the property keys are tuples where the entries are
(*name*, *tag1*).  Now create and write the XML:

    >>> new_xml = wx.New_Xml(xml_type='reaction_data')
    >>> new_xml.set_reaction_data(reactions)
    >>> new_xml.write('new_reaction_data.xml')

Confirm the new XML:

    >>> xml = wx.Xml('new_reaction_data.xml')
    >>> new_reactions = xml.get_reaction_data()
    >>> for r in new_reactions:
    ...     print(r, new_reactions[r].get_data())
    ...

Network XML Data
----------------

For webnucleo codes, a nuclear network is a collection of nuclides and
the reactions among them.  If you have already created or updated
nuclide data *nuclides* and reaction data *reactions* according to the
steps described above, you can create a network XML file.  To do so,
type

    >>> network_xml = wx.New_Xml(xml_type='nuclear_network')

or, simply,

    >>> network_xml = wx.New_Xml()

since the default new XML is of the *nuclear_network* type.  Now
set the data:

    >>> network_xml.set_nuclide_data(nuclides)
    >>> network_xml.set_reaction_data(reactions)

and write the file:

    >>> network_xml.write('new_nuclear_network.xml')

Confirm the new file has the nuclide and reaction data:

    >>> xml = wx.Xml('new_nuclear_network.xml')
    >>> new_nuclides = xml.get_nuclide_data()
    >>> new_reactions = xml.get_reaction_data()
    >>> for nuc in new_nuclides:
    ...     print(nuc)
    ...
    >>> for reaction in new_reactions:
    ...     print(reaction)
    ...

Zone XML Data
-------------

Zone data in webnucleo codes represent mutable data in a calculation.
As with nuclide and reaction data, wnutils routines allow you to update
and create new zone data XML.

Update existing zone data.
..........................

To update zone data, first retrieve the existing data:

    >>> zone_data = old_xml.get_zone_data()

Zones are denoted by up to three labels (*label1*, *label2*, *label3*) given
as either a string or a tuple of strings.,
Each zone can contain *optional_properties* and mass fractions of
nuclear species. To see the available zones, type:

    >>> for zone in zone_data:
    ...     print(zone)
    ,..

Create a new zone that is a copy of the last zone:

    >>> new_zone = zone_data["164"].copy()

Modify a property and a mass fraction in the new zone:

    >>> new_zone['properties']['rho'] = -10
    >>> new_zone['mass fractions'][('he4', 2, 4)] = 0.1

Update the zone data with the new zone:

    >>> zone_data[('165', 'added')] = new_zone

Now write the data to an XML file:

    >>> updated_zone_xml = wx.New_Xml(xml_type='zone_data')
    >>> updated_zone_xml.set_zone_data(zone_data)
    >>> updated_zone_xml.write('updated_zone_data.xml')

Confirm that the new file has the new zone and the updated data:

    >>> xml = wx.Xml('updated_zone_data.xml')
    >>> updated_zone_data = xml.get_zone_data()
    >>> for zone in updated_zone_data:
    ...     print(zone)
    ...
    >>> print(updated_zone_data[('165', 'added')]['properties']['rho'])
    >>> print(updated_zone_data[('165', 'added')]['mass fractions'][('he4', 2, 4)])

Create new zone data.
.....................

To create zone XML data, first create a dictionary of zones:

    >>> zones = {}

Now create property dictionaries for the zones:

    >>> props1 = {'width': 5}
    >>> props2 = {'note': 'This is a note.', ('breadth', 'length', 'width'): 7}

Each dictionary key is either a :obj:`str` or a :obj:`tuple` of strings.
The property value can be any type--it will be converted to a string.
Now create dictionaries of mass fractions:

    >>> mass_frac1 = {('he4', 2, 4): 1}
    >>> mass_frac2 = {('mn53', 25, 53): 0.7, ('fe56', 26, 56): 0.3}

The key for each mass fraction entry is a tuple giving the species *name*,
*Z*, and *A*.  Now create the zones:

    >>> zones["0"] = {'properties': props1, 'mass fractions': mass_frac1}
    >>> zones[("Ringo", "Starr")] = {'properties': {}, 'mass fractions': mass_frac2}
    >>> zones[("John", "Winston", "Lennon")] = {'properties': props2, 'mass fractions': mass_frac2}

Now create the zone data XML, set the data, and write the file:

    >>> zone_xml = wx.New_Xml('zone_data')
    >>> zone_xml.set_zone_data(zones)
    >>> zone_xml.write('new_zone_data.xml')

The file *new_zone_data.xml* contains the data you created.
You can validate it to ensure the data are the right XML format:

    >>> xml = wx.Xml('new_zone_data.xml')
    >>> xml.validate()

Libnucnet XML Data
------------------

Full libnucnet data comprises nuclear network and zone data.  If you
have created nuclide data (*nuclides*), reaction data (*reactions*),
and zone data (*zones*), you can create full libnucnet data by typing:

    >>> libnucnet_xml = wx.New_Xml('libnucnet_input')
    >>> libnucnet_xml.set_nuclide_data(nuclides)
    >>> libnucnet_xml.set_reaction_data(reactions)
    >>> libnucnet_xml.set_zone_data(zones)

Write out the data by typing:

    >>> libnucnet_xml.write('new_libnucnet.xml')



