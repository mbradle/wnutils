Animating the Data
==================

As with plotting,
if you have read in the various data from a webnucleo file, you can
animate them using `matplotlib <https://matplotlib.org>`_.
We have found, however, that it is convenient to have a handful of movie
methods in the `wnutils` API.  This tutorial demonstrates how to use these
methods.  Interested users can, if desired, build their own movie routines
based on the source code of the `wnutils` routines.

Animation writers
-----------------

The default animation writer is `ffmpeg <https://ffmpeg.org>`_.  If you
do not already have it on your system, you should install it.  In linux,
use `apt-get <https://en.wikipedia.org/wiki/APT_(Debian)>`_.  To install,
type::

    $ sudo apt install ffmpeg

On a mac with `MacPorts <https://www.macports.org>`_, type::

    $ sudo port install ffmpeg

On `Cygwin <http://cygwin.org>`_, you will probably have to build it.
For example, see this
`web site <http://www.mediaentertainmentinfo.com/2014/01/1-technical-series-how-to-compile-ffmpeg-under-cygwin.html/>`_.

Setting parameters and methods
------------------------------

Just like the plotting methods,
the animation methods use `rcParams`, `plot parameters`, and `plot methods`.
You can set these as described in the :ref:`plotting` tutorial.

XML
---

To make movies from XML files, import the namespace::

    >>> import wnutils.xml as wx

Then create an object for each file.  For example, type::

    >>> my_xml = wx.Xml('my_output1.xml')

Animating the abundances versus nucleon number
..............................................

To make a movie of the abundances versus mass number, you can type::

    >>> my_xml.make_abundances_vs_nucleon_number_movie('abunds.mp4')

The argument `abunds.mp4` is the name of the movie file that will be
created.  You can add appropriate keyword arguments to adjust the movie
to your taste.  For example, you can type::

    >>> my_xml.make_abundances_vs_nucleon_number_movie('abunds.mp4', xlim = [0,100], ylim = [1.e-10,1], yscale = 'log', xlabel = 'A, Mass Number', ylabel = 'Abundance')

You can add `rcParams` and `plotParams`.  For example, type:

    >>> rc_params = {'lines.linewidth': 2}
    >>> p_params = {'color': 'black'}
    >>> my_xml.make_abundances_vs_nucleon_number_movie('abunds.mp4', rcParams = rc_params, plotParams = p_params, xlim = [0,100], ylim = [1.e-10,1], yscale = 'log', xlabel = 'A, Mass Number', ylabel = 'Abundance')

By default, a title is displayed giving the time in seconds, the temperature
in billions of Kelvins, and the mass density in grams per cc.  You can create
your own title by supplying a title function.  The function must take in
an integer giving the index of a given frame in the movie and must return
a string giving the title or a two-element tuple for which the first element
is the title string and the second is a :obj:`dict` of
:obj:`matplotlib.pyplot.title` keyword options.  The function can also return
`None`, in which case no title is created.  For example, to prevent a title
from appearing in the movie, type::

    >>> def null_title(i):
    ...     return None
    ...
    >>> my_xml.make_abundances_vs_nucleon_number_movie('abunds.mp4', rcParams = rc_params, plotParams = p_params, title_func=null_title, xlim = [0,100], ylim = [1.e-10,1], yscale = 'log', xlabel = 'A, Mass Number', ylabel = 'Abundance')

To make a title that only displays the time and temperature, define the
appropriate title function by typing::

    >>> def my_title(props, i):
    ...     title_str = \
    ...     "time (s) = %8.2e, $T_9$ = %4.2f" % \
    ...     (props['time'][i], props['t9'][i])
    ...     return title_str
    ...

Now bind properties to the function by typing::

    >>> props = my_xml.get_properties_as_floats(['time', 't9'])
    >>> bind = lambda i: my_title(props, i)

Now call the animation routine with the bound function by typing::

    >>> my_xml.make_abundances_vs_nucleon_number_movie('abunds.mp4', rcParams = rc_params, plotParams = p_params, title_func=bind, xlim = [0,100], ylim = [1.e-10,1], yscale = 'log', xlabel = 'A, Mass Number', ylabel = 'Abundance')

If you want to modify the title properties, have the title function return
a tuple.  For example, type::

    >>> def my_title2(props, i):
    ...     title_str = \
    ...     "time (s) = %8.2e, $T_9$ = %4.2f" % \
    ...     (props['time'][i], props['t9'][i])
    ...     return (title_str, {'fontsize': 20, 'color': 'green'})
    ...
    >>> props = my_xml.get_properties_as_floats(['time', 't9'])
    >>> bind = lambda i: my_title2(props, i)
    >>> my_xml.make_abundances_vs_nucleon_number_movie('abunds.mp4', rcParams = rc_params, plotParams = p_params, title_func=bind, xlim = [0,100], ylim = [1.e-10,1], yscale = 'log', xlabel = 'A, Mass Number', ylabel = 'Abundance')

You can plot abundances versus atomic number (`z`) or
neutron number (`n`) by supplying the appropriate keyword.  For example,
type::

    >>> my_xml.make_abundances_vs_nucleon_number_movie('abunds.mp4', nucleon = 'z')

You can also select zones (steps) to plot with an XPath expression.  For
example, type::

    >>> my_xml.make_abundances_vs_nucleon_number_movie('abunds.mp4', nucleon = 'n', zone_xpath = '[position() >= last() - 30]')


That creates a movie of the abundances versus neutron number for the last
30 time steps.  It should be clear that, if you use an XPath expression to
select zones, and if you create your own title from properties, you will need
to use the same XPath expression for the properties to be fed into the
title function.  For example, you could type::

    >>> props = my_xml.get_properties_as_floats(['time','t9'], zone_xpath = '[position() >= last() - 30]')
    >>> bind = lambda i: my_title2(props, i)
    >>> my_xml.make_abundances_vs_nucleon_number_movie('abunds.mp4', nucleon = 'n', zone_xpath = '[position() >= last() - 30]', title_func = bind)

If you do not do this, you will have a mismatch between the frames and their
titles.

You can also add extra curves to the movie that either stay fixed in each frame or vary.  To do so for a fixed curve,
create an array of tuples.  The first element of the tuple gives the array
of abscissa values, the second element gives the array of ordinate values,
and the third element, if provided, gives a dictionary of valid matplotlib
plot options.  Pass the array of tuples into the methods as the keyword
parameter `extraFixedCurves`.  For example, you could type::

    >>> import numpy as np
    >>> ya = my_xml.get_abundances_vs_nucleon_number(zone_xpath = "[position() = 1]")
    >>> my_extra = [(np.arange(len(ya[0])), ya[0], {'lw': 0.3, 'color': 'blue', 'label': 'Initial'})]
    >>> anim = my_xml.make_abundances_vs_nucleon_number_movie(extraFixedCurves=my_extra, yscale = 'log', ylim = [1.e-10,1], plotParams={'label': 'Current'}, legend={'loc': 'upper right'})

This returns the animation.  You can the write a movie by typing::

    >>> anim.save('abunds.mp4', fps = 15)

Of course, you can also pass the movie name in as the first parameter or as a
keyword to make the movie directly::

    >>> my_xml.make_abundances_vs_nucleon_number_movie(movie_name = 'abunds.mp4', extraFixedCurves=my_extra, yscale = 'log', ylim = [1.e-10,1], plotParams={'label': 'Current'}, legend={'loc': 'upper right'})

Animating an abundance chain
............................

An abundance chain is the collection of abundances along a fixed `Z` or `N`.
To make a movie of an abundance chain, type::

    >>> my_xml.make_abundance_chain_movie('abund_chain.mp4')

The argument `abund_chain.mp4` is the name of the movie file that will be
created.  The default is to plot along the fixed `Z = 26` chain.  To plot against
a different `Z`, use the `nucleon` keyword to enter a tuple.  For example, to plot
for `Z = 30`, type::

    >>> my_xml.make_abundance_chain_movie(movie_name = 'abund_chain.mp4', nucleon=('z', 30), plot_vs_A=True)

The `plot_vs_A` keyword causes the abscissa to be mass number instead of neutron
number.  To plot for `N = 30`, type::

    >>> my_xml.make_abundance_chain_movie('abund_chain.mp4', nucleon=('n', 30), plot_vs_A=True)

As with the abundances versus nucleon number movie,
you can add appropriate keyword arguments and extra curves to adjust the movie
to your taste.  For example, you can type::

    >>> my_nucleon = ('z', 28)
    >>> x, y = my_xml.get_chain_abundances(my_nucleon, zone_xpath="[last()]")
    >>> extra_curve = [(x, y[0], {'lw': 0.5, 'label': 'Final', 'color': 'red'})]
    >>> my_xml.make_abundance_chain_movie('abund_chain.mp4', nucleon = my_nucleon, xlim = [20, 50], ylim = [1.e-10,1], yscale = 'log', xlabel = 'N, Neutron Number', ylabel = 'Abundance', extraFixedCurves = extra_curve, plotParams = {'label': 'Current'}, legend={'loc': 'upper right'})

You can also adjust the title by defining a title function and binding, as with the
nucleon number movie.

Animating the network abundances
................................

You can animate the network abundances in the neutron number-proton number
plane.  For example, type::

    >>> my_xml.make_network_abundances_movie('network_abunds.mp4')

The black curves in the movie show the network limits.  The properties of
those lines are set with `plotParams`.  To see how this works, type::

    >>> my_xml.make_network_abundances_movie('network_abunds.mp4', plotParams={'color': 'green', 'linestyle': 'dotted'})

The routine takes keyword arguments, as usual.  For example, type::

    >>> my_xml.make_network_abundances_movie('network_abunds.mp4', xlim=[0,60], ylim = [0,50])

The abundances are shown by the blue-purple color intensity.  The details
are set by the keyword argument `imParams`, which is a :obj:`dict` of
valid :obj:`matplotlib.pyplot.imshow` options.  The default is as if you
had called the routine with imParams={'origin':'lower', 'cmap': cm.BuPu,
'norm': LogNorm(), 'vmin': 1.e-10, 'vmax': 1}, which shows that the abundances
are displayed on a logarithmic scale with maximum value 1 and minimum value
1.e-10.  We can override any or all of these.  For example, to change the
minimum abundance to 1.e-15 and the color map to reds, type::

    >>> import matplotlib.cm as cm
    >>> my_xml.make_network_abundances_movie('network_abunds.mp4', xlim=[0,60], ylim = [0,50], imParams = {'cmap': cm.Reds, 'vmin': 1.e-15})

It is often desirable to add a colorbar.  For example, you can create
colorbar properties by typing::

    >>> cb = {'shrink': 0.85, 'label': 'Abundance', 'aspect': 10, 'ticks': [1.e-10, 1.e-8, 1.e-6, 1.e-4, 1.e-2, 1.]}

The arguments to the colorbar properties are any valid
:obj:`matplotlib.pyplot.colorbar` optional keyword argument.  You can now
type::

    >>> my_xml.make_network_abundances_movie('network_abunds.mp4', xlim=[0,60], ylim = [0,50], colorbar = cb)

Of course, you will want to make sure that your ticks in the colorbar are
consistent with your limits.  For example, you can type::

    >>> cb = {'shrink': 0.85, 'label': 'Abundance', 'aspect': 10, 'ticks': [1.e-15, 1.e-10, 1.e-5, 1.]}
    >>> my_xml.make_network_abundances_movie('network_abunds.mp4', xlim=[0,60], ylim = [0,50], imParams = {'cmap': cm.Reds, 'vmin': 1.e-15}, colorbar = cb)

As with the routine to animate abundances versus nucleon number, you can
use `zone_xpath` to select steps and `title_func` to define your own title
string.  For example, if you defined `my_title2()` as above, you can type::

    >>> props = my_xml.get_properties_as_floats(['time','t9'])
    >>> bind = lambda i: my_title(props, i)
    >>> my_xml.make_network_abundances_movie('network_abunds.mp4', xlim=[0,60], ylim = [0,50], imParams = {'cmap': cm.Reds, 'vmin': 1.e-15}, colorbar = cb, title_func = bind)
	
H5
--

To make movies from HDF5 files, import the namespace::

    >>> import wnutils.h5 as w5

Then create an object for each file.  For example, type::

    >>> my_h5 = w5.H5('my_output1.h5')

Animating the mass fractions in zones
.....................................

Most commonly one writes out HDF5 files for multi-zone network calculations.
The output in `my_output1.h5` and `my_output2.h5` is for one-dimensional
multi-zone network calculations in which matter burns in the individual
zones and mixes between the zones.  In such calculations, one generally
wants to see the evolution of the mass fractions
in the zones as a function of time.  To see an example of how you can do this,
type::

    >>> my_h5.make_mass_fractions_movie(['o16','ne20'], 'mass_fracs.mp4')

This creates a movie `mass_fracs.mp4` of o16 and ne20 in the zones as a
function of time.  The
x axis shows zone indices.  The y axis gives mass fractions.  The scale
of the y axis changes.  Since you probably want that fixed, call with
keyword arguments.  For example, you can type::

    >>> my_h5.make_mass_fractions_movie(['o16','ne20'], 'mass_fracs.mp4', ylim = [1.e-10,1], yscale = 'log', ylabel = 'Mass Fraction')

To keep the legend from moving, call with the `legend` keyword.  For example,
type::

    >>> my_h5.make_mass_fractions_movie(['o16','ne20'], 'mass_fracs.mp4', ylim = [1.e-10,1], yscale = 'log', ylabel = 'Mass Fraction', legend={'loc': 'lower right'})

To use your own title, define a title function as before.  For example,
to change from seconds to years, type::

    >>> def my_time_title(props, i):
    ...     title_str = "time (yr) = %8.2e" % (props['time'][i] / 3.15e7)
    ...     return title_str
    ... 

Next, bind data to the function by typing::

    >>> zone = ('0','0','0')
    >>> props = my_h5.get_zone_properties_in_groups_as_floats( zone, ['time'] )
    >>> bind = lambda i: my_time_title(props, i)

Now you can call the routine with the title function by typing::

    >>> my_h5.make_mass_fractions_movie(['o16','ne20'], 'mass_fracs.mp4', ylim = [1.e-10,1], yscale = 'log', ylabel = 'Mass Fraction', legend={'loc': 'lower right'}, title_func=bind, use_latex_names=True)

This example also labels the species with superscripts for the species
mass number.

You can also plot the zone abundances against a zone property.  Since each
zone in `my_output1.h5` has a temperature, you can plot against that by typing::

    >>> my_h5.make_mass_fractions_movie(['o16','ne20'], 'mass_fracs.mp4', property='t9', ylim = [1.e-10,1], yscale = 'log', ylabel = 'Mass Fraction', legend={'loc': 'lower right'}, title_func=bind, use_latex_names=True, xlim=[0.3,0], xlabel='$T_9$')

Notice the `xlim` to get the temperatures oriented correctly with zone index.

As with other movies, you can call the routine with `rcParams` and `plotParams`,
as desired.
