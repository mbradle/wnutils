.. _plotting:

Plotting the Data
==================

If you have read in the various data from a webnucleo file, you can
plot them using `matplotlib <https://matplotlib.org>`_.  For example, to
plot the abundance of Z=28 nuclei in `my_output1.xml` as a function of time,
you can type in Python::

    >>> import matplotlib.pyplot as plt
    >>> import wnutils.xml as wx
    >>> my_xml = wx.Xml('my_output1.xml')
    >>> props = my_xml.get_properties_as_floats(['time'])
    >>> yz = my_xml.get_abundances_vs_nucleon_number(nucleon='z')
    >>> plt.plot(props['time'],yz[:,28])
    >>> plt.xscale('log')
    >>> plt.xlim([1.e-14,1.])
    >>> plt.ylim([0.,0.0014])
    >>> plt.xlabel('time (s)')
    >>> plt.ylabel('Y(28)')
    >>> plt.show()

Of course you can also write a Python file (called, say, my_plot.py)
with the above lines and execute it by typing `python my_plot.py`.

While it is always possible to make such plots with data read in with `wnutils`
routines, we have written several plotting methods for commonly made plots.  The
rest of this tutorial demonstrates how to use these methods.

Setting RcParams
----------------

All the plotting methods accept RcParams as keywords.  These can be entered as
a key and value pair or as a dictionary of :obj:`matplotlib.RcParams`.  You can
print the list of parameters (and their default values) that can be set by typing::

    >>> import wnutils.base as wnb
    >>> wb = wnb.Base()
    >>> wb.list_rcParams()

Since the Base class is inherited by the other wnutils classes, the
`list_rcParams()` method is available from any class instance.

For the purposes of this tutorial,
define a dictionary of parameters by typing::

    >>> my_params = {'lines.linewidth': 2, 'font.size': 14}

Setting plot parameters
-----------------------

The plotting methods accept `plotParams` as a keyword.  The object
passed in through the keyword is a :obj:`dict`
of :obj:`matplotlib.pyplot.plot` optional keyword arguments.
The dictionary values govern
the lines drawn on the plot.  For example, calling a `wnutils`
plotting routine with

    >>> params = {'color':'black'}

and then `plotParams = params` in the plotting routine can be thought of
as plotting with the command::

    >>> import matplotlib.pyplot as plt
    >>> plt.plot(x, y, color='black')

When the plotting routine creates multiple curves on the same plot,
the object passed in
through `plotParams` is a :obj:`list` of dictionaries
of :obj:`matplotlib.pyplot.plot` optional keyword arguments.
Each dictionary in the list corresponds to a curve on the plot.

Setting plot methods
--------------------

The plotting routines also accept keywords giving :obj:`matplotlib.pyplot`
methods and their arguments.  In such a case, the keyword is the method,
and the value is the argument to the method.  For example,
calling a `wnutils` plotting routine with the
keyword `xlabel = 'time (s)'` is equivalent to typing::

    >>> import matplotlib.pyplot as plt
    >>> plt.xlabel('time (s)')

These can be entered directly or as a dictionary.  If the method takes
an argument and optional keywords, enter these as a tuple.  For example,
calling a `wnutils` plotting routine with the keyword
`savefig = ('my_fig.png', {'bbox_inches': 'tight'})` is equivalent to typing::

    >>> plt.savefig('my_fig.png', bbox_inches = 'tight')

The tuple must have two elements--the argument and the dictionary of optional
keyword arguments.

XML
---

To make graphs from XML files, first import the namespace::

    >>> import wnutils.xml as wx

Then create an object for each file.  For example, type::

    >>> my_xml = wx.Xml('my_output1.xml')

Plot properties against each other for the zones.
.................................................

You can plot properties in the zones in an XML file against each other.  For
example, to plot `t9` vs. `time`, type::

    >>> my_xml.plot_property_vs_property( 'time', 't9' )

Now apply class methods to the plot.  For example, type::

    >>> my_xml.plot_property_vs_property( 'time', 't9', xlabel = 'time (s)', ylabel = '$T_9$' )

You can equivalently do this by defining the method keywords in a dictionary and
calling that.  To do so, type::

    >>> kw = {'xlabel':'time (s)', 'ylabel':'$T_9$'}
    >>> my_xml.plot_property_vs_property('time', 't9', **kw)

You can also do this with both procedures.  For example, type::

    >>> kw2 = {'xlabel':'time (s)'}
    >>> my_xml.plot_property_vs_property('time', 't9', ylabel = '$T_9$', **kw2)

You can call with the RcParams previously defined by typing::

    >>> my_xml.plot_property_vs_property('time', 't9', rcParams=my_params, **kw)

You can also call the the plotParams keyword by typing::

    >>> my_xml.plot_property_vs_property('time', 't9', rcParams=my_params, plotParams={'color':'black'}, **kw)

Plot mass fractions against a property.
.........................................

You can plot mass fractions of species against a property (typically the time
or temperature).  For example, to plot the mass fractions of he4 and fe58 
versus time, type::

    >>> my_xml.plot_mass_fractions_vs_property( 'time', ['he4','fe58'] )

You can add appropriate keywords.  For example, you can type::

    >>> my_xml.plot_mass_fractions_vs_property( 'time', ['he4','fe58'], use_latex_names=True, xlabel = 'time (s)', xlim=[1.e-6,1], xscale = 'log', ylim=[0,1])

By setting the `use_latex_names` keyword to true, species names appear as
a superscript mass number in front of the element name.  You can of course also
use the RcParams::

    >>> my_xml.plot_mass_fractions_vs_property( 'time', ['he4','fe58'], use_latex_names=True, xlabel = 'time (s)', xlim=[1.e-6,1], xscale = 'log', ylim=[0,1], rcParams=my_params)

If you want to plot the mass fraction for a single species,
be sure to enter that species as a list of one element::

    >>> kw3 = {'use_latex_names': True, 'xlabel': '$T_9$', 'xlim': [10,0]}
    >>> my_xml.plot_mass_fractions_vs_property( 't9', ['si28'], **kw3, ylim=[1.e-12,1.e-4], yscale = 'log')

Finally, note that you can define the species to plot as a list that you then
enter into the plot command.  For example, type::

    >>> nuclides_list = ['fe56','fe57','fe58']
    >>> my_xml.plot_mass_fractions_vs_property( 'time', nuclides_list, use_latex_names=True, xlabel = 'time (s)', xlim=[1.e-6,1], xscale = 'log', ylim=[0,0.5], rcParams=my_params)

You can generate the list from an XPath expression.  For example, try typing::

    >>> nuclides = my_xml.get_nuclide_data(nuc_xpath='[z = 26 and (a - z >= 30 and a - z <= 32)]')
    >>> nuclides_list = []
    >>> for nuclide in nuclides:
    ...     nuclides_list.append(nuclide)
    ...
    >>> print(nuclides_list)

Now you can use that list in the plotting routine.

Plot abundances versus nucleon number.
......................................

To plot the summed abundances over mass number A in the last zone, type::

    >>> my_xml.plot_abundances_vs_nucleon_number()

To dress that up, try typing::

    >>> my_xml.plot_abundances_vs_nucleon_number(xlim = [0,100], ylim = [1.e-10,1], yscale='log', xlabel = 'Mass Number, A', ylabel = 'Y(A)')

Use keywords to plot against atomic number (Z) or neutron number (N) or to plot
against a different time step (zone), using an XPath expression.  For example,
to plot elemental abundances in the 20th step, type::

    >>> my_xml.plot_abundances_vs_nucleon_number(nucleon='z', zone_xpath='[position() = 20]', xlim = [0,50], ylim = [1.e-10,1], yscale='log', xlabel = 'Atomic Number, Z', ylabel = 'Y(Z)')

To add a title giving the conditions at that step, type::

    >>> props = my_xml.get_properties_as_floats( ['time','t9','rho'] )
    >>> title_str = 'time(s) = {0:.2e}, t9 = {1:.2f}, rho(g/cc) = {2:.2e}'.format(
    ...                 props['time'][19], props['t9'][19], props['rho'][19]
    ...             )
    >>> my_xml.plot_abundances_vs_nucleon_number(nucleon='z', zone_xpath='[position() = 20]', xlim = [0,50], ylim = [1.e-10,1], yscale='log', xlabel = 'Atomic Number, Z', ylabel = 'Y(Z)', title=title_str)

Recall that the property arrays are
`zero-indexed <https://en.wikipedia.org/wiki/Zero-based_numbering>`_.

You can plot more than one time step (zone) by using an XPath expression.
For example, to plot the first and last time steps, type::

    >>> my_xml.plot_abundances_vs_nucleon_number(zone_xpath='[(position() = 1) or (position() = last())]', yscale = 'log', ylim = [1.e-10,1])

Use a list of plot parameters to label the steps and other keywords to
give the plot the desired look::

    >>> p_params = [{'label': 'first'}, {'label': 'last'}]
    >>> my_xml.plot_abundances_vs_nucleon_number(zone_xpath='[(position() = 1) or (position() = last())]', plotParams = p_params, yscale = 'log', ylim = [1.e-10,1], xlabel = 'A, Mass Number', ylabel = 'Y(A)', xlim = [0,100], legend = {'title': 'time step', 'shadow': True})

It is also possible to label the steps with the legend keyword.  To do this,
type::

    >>> my_xml.plot_abundances_vs_nucleon_number(zone_xpath='[(position() = 1) or (position() = last())]', yscale = 'log', ylim = [1.e-10,1], xlabel = 'A, Mass Number', ylabel = 'Y(A)', xlim = [0,100], legend = (['first','last'], {'title': 'time step', 'shadow': True}))

You can save the figure as a file, for example, by typing::

    >>> my_xml.plot_abundances_vs_nucleon_number(zone_xpath='[(position() = 1) or (position() = last())]', yscale = 'log', ylim = [1.e-10,1], xlabel = 'A, Mass Number', ylabel = 'Y(A)', xlim = [0,100], legend = (['first','last'], {'title': 'time step', 'shadow': True}), savefig = ('my_fig.png', {'bbox_inches': 'tight'}))

Multi_XML
---------

To make plots from multiple webnucleo XML files, first import the namespace::

    >>> import wnutils.multi_xml as mx

Next, create an object for the files:

    >>> my_multi_xml = mx.Multi_Xml(['my_output1.xml', 'my_output2.xml'])

Plot a property against a property in multiple files.
.....................................................

You can plot a property versus another property in multiple files.  For
example, to plot the `t9` versus `time` in our two files, type::

    >>> my_multi_xml.plot_property_vs_property('time','t9')

Since the calculations are for different exponential expansion timescales,
you can label them with a legend.  First, find the timescale by noting
that :math:`\rho(t) = \rho(0) \exp(-t/\tau)`.  This means that
:math:`\tau = -t\ /\ln\left(\rho(t)/\rho(0)\right)`.  Choose, say, step 150 to
compute the `tau` for the two calcluations.  You can type::

    >>> import math
    >>> xmls = my_multi_xml.get_xml()
    >>> p_params = []
    >>> for xml in xmls:
    ...     props = xml.get_properties_as_floats(['time','rho'])
    ...     tau = -props['time'][150] / math.log(props['rho'][150]/props['rho'][0])
    ...     p_params.append({'label':('{:8.2f}'.format(tau)).strip() + 's'})
    ... 

Now call the plot method with the plotParams keyword by typing::

    >>> my_multi_xml.plot_property_vs_property('time','t9', plotParams = p_params, legend={'title':'tau'})

Notice the call to the legend keyword.  The keyword values can be any
valid keyword argument to :obj:`matplotlib.pyplot.legend`.  Thus, for example,
you could type::

    >>> my_multi_xml.plot_property_vs_property('time','t9', plotParams = p_params, legend={'title':'tau', 'shadow':True})

Plot a mass fraction against a property in multiple files.
..........................................................

You can also plot a mass fraction versus a property in multiple files.
For example, to plot the mass fraction of fe58 as a function of time
(and using the labels you defined above), type::

    >>> my_multi_xml.plot_mass_fraction_vs_property('time', 'fe58', plotParams = p_params, legend={'title':'tau'})

:obj:`wnutils.multi_xml.Multi_Xml` plotting methods accept valid `rcParams` and
other keywords, as in the :obj:`wnutils.xml.Xml` methods.

H5
----

To make plots from webnucleo HDF5 file, first import the namespace::

    >>> import wnutils.h5 as w5

Next, create an object for each file by typing::

    >>> my_h5 = w5.H5('my_output1.h5')

Plot a property versus a property for a given zone.
...................................................

You can plot the values of two properties in all groups
against each other for a given zone.  For
example, to plot `t9` versus `time` in the zone with labels `2`, `0`, `0`,
type::

    >>> zone = ('2','0','0')
    >>> kws = {'xlabel': 'time (yr)', 'ylabel': '$T_9$'}
    >>> my_h5.plot_zone_property_vs_property(zone, 'time', 't9', xfactor=3.15e7, **kws)

In the calculation that gave the output in `my_output1.h5`,
the temperature and density in zones were constant in time.

Plot mass fractions versus a property for a given zone.
.......................................................

You can plot mass fractions against a property for a given zone.  For example,
type::

     >>> my_h5.plot_zone_mass_fractions_vs_property(
     ...     ('1','0','0'), 'time', ['he4', 'c12','o16'], yscale = 'log',
     ...      ylim = [1.e-5,1], xscale = 'log', xlim = [1,1.e5], xfactor = 3.15e7,
     ...      xlabel = 'time (yr)', use_latex_names=True
     ... )

Note, this is equivalent to typing::

     >>> zone = ('1','0','0')
     >>> species = ['he4','c12','o16']
     >>> kwa = {'xlim': [1,1.e5], 'ylim': [1.e-5,1]}
     >>> kwb = {'xscale': 'log', 'yscale': 'log', 'xfactor': 3.15e7}
     >>> kwc = {'xlabel': 'time (yr)', 'use_latex_names': True}
     >>> my_h5.plot_zone_mass_fractions_vs_property( zone, 'time', species, **kwa, **kwb, **kwc)

Or, in Python 3.5 or greater, you can type::

     >>> kws = {**kwa,**kwb,**kwc}
     >>> my_h5.plot_zone_mass_fractions_vs_property( zone, 'time', species, **kws)

Plot a property in the zones of a given group.
..............................................

To plot a property in all the zones of a given group, say, Step number 125,
you can, for example, type::

    >>> my_h5.plot_group_property_in_zones('Step 00125', 't9')

This shows the temperature (in billions of Kelvins) in the zones.  The
innermost (first) zone is the hottest.

Plot mass fractions for a given group.
......................................

You can plot the mass fractions for a given group.  The abscissa of the
plot in this case will be a zone index.  For example, type::

     >>> my_h5.plot_group_mass_fractions(
     ...     'Step 00125', ['he4', 'c12','o16'], use_latex_names=True
     ... )

Plot group mass fractions versus a property.
............................................

In the previous example, you simply plotted the mass fractions against
their zone.  You can also plot against a zone property.  For example,
type::

     >>> my_h5.plot_group_mass_fractions_vs_property(
     ...     'Step 00125', 't9', ['he4', 'c12','o16'], use_latex_names=True
     ... )

Notice that the plot shows the lowest temperature zone to the right part
of the plot.  To show the graph with the innermost (hottest) zones plotted
to the right, use the `xlim` keyword::

     >>> my_h5.plot_group_mass_fractions_vs_property(
     ...     'Step 00125', 't9', ['he4', 'c12','o16'], use_latex_names=True, xlim = [0.3,0]
     ... )

Multi_H5
---------

To make plots from multiple webnucleo HDF5 files, first import the namespace::

    >>> import wnutils.multi_h5 as m5

Next, create an object for the files:

    >>> my_multi_h5 = m5.Multi_H5(['my_output1.h5', 'my_output2.h5'])

Plot a zone property against a property in multiple files.
..........................................................

You can plot a property versus another property in multiple files.  For
example, to plot the `neutron exposure` versus `time` in our two files, type::

    >>> zone = ('0','0','0')
    >>> my_multi_h5.plot_zone_property_vs_property(zone, 'time',('exposure', 'n'))

Notice that the `neutron exposure` property is input as a tuple
because, in this case, the property identifier has two parts: a `name` string
('exposure') and a `tag1` string ('n').
As discussed in the :ref:`reading` tutorial,
a property can have a name
and up to two tags; thus, the tuple identifying the property could have
up to three elements.  The neutron exposure is usually
labeled :math:`\tau_n` and has units of :math:`mb^{-1}`, that is,
inverse `millibarns <https://en.wikipedia.org/wiki/Barn_(unit)>`_.
The difference in the two calculations
is that the first was for a mixing timescale of 10\ :sup:`7` seconds while the
second was for a mixing timescale of 10\ :sup:`9` seconds.  We can thus add
a legend by typing::

    >>> p_params = [{'label':'$10^7\ s$', 'color':'black', 'linestyle':'-'}, {'label':'$10^9\ s$', 'color':'black', 'linestyle':':'}]

Now call the plot method with the plotParams keyword by typing::

    >>> my_multi_h5.plot_zone_property_vs_property(
    ...     zone, 'time',('exposure', 'n'), plotParams = p_params, legend={'title':'$\\tau_{mix}$'},
    ...     xlabel='time (yr)', xfactor=3.15e7, ylabel='$\\tau_n(mb^{-1})$'
    ... )

As with :obj:`wnutils.multi_xml`, the legend keyword values can be any
valid keyword argument to :obj:`matplotlib.pyplot.legend`.  Thus, for example,
you could type::

    >>> my_multi_h5.plot_zone_property_vs_property(
    ...     zone, 'time',('exposure', 'n'), plotParams = p_params,
    ...     legend={'title':'$\\tau_{mix}$', 'shadow':True},
    ...     xlabel='time (yr)', xfactor=3.15e7, ylabel='$\\tau_n(mb^{-1})$'
    ... )

Plot a zone mass fraction against a property in multiple files.
...............................................................

You can also plot a mass fraction versus a property in multiple files.
For example, to plot the mass fraction of fe56 as a function of time,
type::

    >>> my_multi_h5.plot_zone_mass_fraction_vs_property(zone, 'time', 'fe56', plotParams = p_params, legend={'title':'$\\tau_{mix}$'})

:obj:`wnutils.multi_h5.Multi_H5` plotting methods accept valid `rcParams` and
other keywords, as in the :obj:`wnutils.h5.H5` methods.

