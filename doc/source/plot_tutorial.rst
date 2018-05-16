Plotting the Data
==================

XML
---

Plot properties against each other for the zones.
.................................................

Type::

     >>> import wnutils.plot.xml as wp
     >>> wp.plot_property_vs_property( 'my_output1.xml', 'time', 't9' )

Plot mass fractions against a property.
.........................................

Type::

     >>> import wnutils.plot.xml as wp
     >>> wp.plot_mass_fractions_vs_property( 'my_output1.xml', 'time', ['he4','fe58'] )



