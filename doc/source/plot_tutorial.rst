Plotting the Data
==================

XML
---

Import the namespace::

     >>> import wnutils.xml as wx

The create an object for each file.  For example, type::

    >>> my_xml = wx.Xml('my_output1.xml')

Plot properties against each other for the zones.
.................................................

Type::

    >>> my_xml.plot_property_vs_property( 'time', 't9' )

Plot mass fractions against a property.
.........................................

Type::

    >>> my_xml.plot_mass_fractions_vs_property( 'time', ['he4','fe58'] )


HDF5
----

Import the namespace::

    >>> import wnutils.h5 as w5

Create an object for each file by typing::

    >>> my_h5 = w5.H5( 'my_output.h5' )

Plot mass fractions versus a property for a given zone.
.......................................................

Type::

     >>> w5.plot_zone_mass_fractions_vs_property(
     ...     ('1','0','0'), 'time', ['he4', 'c12','o16'], yscale = 'log',
     ...      ylim = [1.e-5,1], xscale = 'log', xlim = [1,1.e5], xfactor = 3.15e7,
     ...      xlabel = 'time (yr), use_latex_names=True
     ... )
     ...

Plot mass fractions for a given group.
......................................

Type::

     >>> w5.plot_group_mass_fractions(
     ...     'Step 00025', ['he4', 'c12','o16'], use_latex_names=True
     ... )
     ...

