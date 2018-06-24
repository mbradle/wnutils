Animating the Data
==================

As with plotting,
if you have read in the various data from a webnucleo file, you can
animate them using `matplotlib <https://matplotlib.org>`_.
We have found, however, that it is convenient to have a number of movie methods
in the ``wnutils`` API.  This tutorial demonstrates how to use these
methods.

Animation writers
-----------------

The default animation writer is `ffmpeg <https://ffmpeg.org>`_.  You should
install it.  In linux,
use `apt-get <https://en.wikipedia.org/wiki/APT_(Debian)>`_.  To install,
type::

    $ sudo apt install ffmpeg

On a mac with `Mac Ports <https://www.macports.org>`_, type::

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
----------------------------------------------

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
