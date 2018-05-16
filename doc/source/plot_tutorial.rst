Plotting the Data
==================

XML
---

Import the namespace::

     >>> import wnutils.plot.xml as wpx

Plot properties against each other for the zones.
.................................................

Type::

     >>> wpx.plot_property_vs_property( 'my_output1.xml', 'time', 't9' )

Plot mass fractions against a property.
.........................................

Type::

     >>> wpx.plot_mass_fractions_vs_property( 'my_output1.xml', 'time', ['he4','fe58'] )


HDF5
----

Import the namespace::

     >>> import wnutils.plot.h5 as wp5

Plot mass fractions versus a property for a given zone.
.......................................................

Type::

     >>> wp5.plot_zone_mass_fractions_vs_property(
     ...     'my_output.h5', ('1','0','0'), 'time', ['he4', 'c12','o16'], yscale = 'log',
     ...      ylim = [1.e-5,1], xscale = 'log', xlim = [1,1.e5], xfactor = 3.15e7,
     ...      xlabel = 'time (yr), use_latex_names=True
     ... )
     ...

Plot mass fractions for a given group.
......................................

Type::

     >>> wp5.group_mass_fractions(
     ...     'my_output.h5', 'Step 00025', ['he4', 'c12','o16'], use_latex_names=True
     ... )
     ...

