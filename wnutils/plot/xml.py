import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

import wnutils.read.xml as wx
import wnutils.params as plp
import wnutils.utils as wu


def plot_mass_fraction_vs_property_in_files(
    files, prop, species, legend_labels=None, xfactor=1,
    use_latex_names=False, rcParams=None, **kwargs
):
    """Function to plot the mass fraction of a species in multiple files.

    Args:
        ``files`` (:obj:`list`): A list of strings giving the files.

        ``prop`` (:obj:`str`): A string giving the property (which will be the
        abscissa of the plot).

        ``species`` (:obj:`str`):  A string giving the species.

        ``legend_labels`` (:obj:`list`, optional): A list of strings giving
        the legend labels.  Defaults to None.

        ``xfactor`` (:obj:`float`, optional): A float giving the scaling for
        the abscissa values.  Defaults to 1.

        ``use_latex_names`` (:obj:`bool`, optional): If set to True, and if
        ylabel not set in kwargs, converts ordinate label to latex format.

        ``rcParams`` (:obj:`dict`, optional): A dictionary of
        :obj:`matplotlib.rcParams` to be applied to the plot.
        Defaults to leaving the current rcParams unchanged.

        ``**kwargs``:  Acceptable :obj:`matplotlib.pyplot` functions.  Include
        directly, as a :obj:`dict`, or both.

    Returns:
        A matplotlib plot.

    Example:

        >>> import wnutils.plot.xml as wp
        >>> files = ['file1.xml', 'file2.xml', 'file3.xml']
        >>> my_params = {'lines.linewidth': 3, 'legend.loc': 'center right' }
        >>> kw = {'xlabel': 'time (s)'}
        >>> wp.plot_mass_fraction_vs_property_in_files(
        ...     files,
        ...     'time',
        ...     'o16',
        ...     legend_labels = ['file1', 'file2', 'file3'],
        ...     use_latex_names = True,
        ...     rcParams = my_params,
        ...     ylim = [1.e-4,1],
        ...     **kw
        ... )
        ...

    """
    plp.set_plot_params(mpl, rcParams)

    if legend_labels:
        if(len(legend_labels) != len(files)):
            print("Invalid legend labels for input files.")
            return

    fig = plt.figure()

    for i in range(len(files)):
        x = wx.get_properties_in_zones_as_floats(files[i], [prop])[prop]
        x /= xfactor
        y = wx.get_mass_fractions_in_zones(files[i], [species])[species]
        if legend_labels:
            ll, = plt.plot(x, y, label=legend_labels[i])
        else:
            ll, = plt.plot(x, y)

    plp.apply_class_methods(plt, kwargs)

    if use_latex_names:
        if 'ylabel' not in kwargs:
            plt.ylabel(
                'X(' + wu.get_latex_names([species])[species] + ')'
            )

    if legend_labels:
        plt.legend()

    plt.show()


def plot_mass_fractions_in_zones(
    file, species, use_latex_names=False, rcParams=None, **kwargs
):
    """Function to plot the mass fractions in zones.

    Args:
        ``files`` (:obj:`str`): A string giving the xml file.

        ``species``:obj:`list`):  A list of strings giving the species.

        ``use_latex_names`` (:obj:`bool`, optional): If set to True,
        converts species labels to latex format.

        ``rcParams`` (:obj:`dict`, optional): A dictionary of
        :obj:`matplotlib.rcParams` to be applied to the plot.
        Defaults to leaving the current rcParams unchanged.

        ``**kwargs``:  Acceptable :obj:`matplotlib.pyplot` functions.  Include
        directly, as a :obj:`dict`, or both.

    Returns:
        A matplotlib plot.

    Example:

        >>> import wnutils.plot.xml as wp
        >>> my_params = {'lines.linewidth': 3, 'legend.loc': 'center right' }
        >>> wp.plot_mass_fractions_in_zones(
        ...     'my_output.xml',
        ...     ['si28','ni56'],
        ...     use_latex_names = True,
        ...     rcParams = my_params,
        ...     ylim = [1.e-4,1]
        ... )
        ...

    """

    plp.set_plot_params(mpl, rcParams)

    fig = plt.figure()

    y = []
    l = []
    latex_names = []

    y = wx.get_mass_fractions_in_zones(file, species)

    if use_latex_names:
        latex_names = wu.get_latex_names(species)

    for i in range(len(species)):
        if(len(latex_names) != 0):
            lab = latex_names[species[i]]
        else:
            lab = species[i]
        l.append(plt.plot(y[species[i]], label=lab))

    if('ylabel' not in kwargs):
        if(len(species) != 1):
            plt.ylabel('Mass Fraction')
        else:
            if(len(latex_names) == 0):
                plt.ylabel('X(' + species[0] + ')')
            else:
                plt.ylabel('X(' + latex_names[species[0]] + ')')

    if('xlabel' not in kwargs):
        plt.xlabel('step')

    plp.apply_class_methods(plt, kwargs)

    plt.show()


def plot_mass_fractions_vs_property(
    file, prop, species, xfactor=1, use_latex_names=False, rcParams=None,
    **kwargs
):
    """Function to plot the mass fractions versus a property.

    Args:
        ``files`` (:obj:`str`): A string giving the xml file.

        ``prop`` (:obj:`str`): A string giving the property (which will be the
        abscissa of the plot).

        ``species``:obj:`list`):  A list of strings giving the species.

        ``xfactor`` (:obj:`float`, optional): A float giving the scaling for
        the abscissa values.  Defaults to 1.

        ``use_latex_names`` (:obj:`bool`, optional): If set to True,
        converts species labels to latex format.

        ``rcParams`` (:obj:`dict`, optional): A dictionary of
        :obj:`matplotlib.rcParams` to be applied to the plot.
        Defaults to leaving the current rcParams unchanged.

        ``**kwargs``:  Acceptable :obj:`matplotlib.pyplot` functions.  Include
        directly, as a :obj:`dict`, or both.

    Returns:
        A matplotlib plot.


    Example:

        >>> import wnutils.plot.xml as wp
        >>> my_params = {'lines.linewidth': 3, 'legend.loc': 'center right' }
        >>> kw = {'xlabel': 'time (yr)'}
        >>> wp.plot_mass_fractions_vs_property(
        ...     'my_output.xml',
        ...     'time',
        ...     ['c12','o16'],
        ...     use_latex_names = True,
        ...     xfactor = 3.15e7,
        ...     rcParams = my_params,
        ...     ylim = [1.e-4,1],
        ...     **kw
        ... )
        ...

    """

    plp.set_plot_params(mpl, rcParams)

    fig = plt.figure()

    y = []
    l = []
    latex_names = []

    x = (wx.get_properties_in_zones_as_floats(file, [prop]))[prop] / xfactor

    y = wx.get_mass_fractions_in_zones(file, species)

    if use_latex_names:
        latex_names = wu.get_latex_names(species)

    for i in range(len(species)):
        if(len(latex_names) != 0):
            lab = latex_names[species[i]]
        else:
            lab = species[i]
        l.append(plt.plot(x, y[species[i]], label=lab))

    if('ylabel' not in kwargs):
        if(len(species) != 1):
            plt.ylabel('Mass Fraction')
        else:
            if(len(latex_names) == 0):
                plt.ylabel('X(' + species[0] + ')')
            else:
                plt.ylabel('X(' + latex_names[species[0]] + ')')

    if len(species) != 1:
        plt.legend()

    if('xlabel' not in kwargs):
        plt.xlabel(prop)

    plp.apply_class_methods(plt, kwargs)

    plt.show()


def plot_property_vs_property(
    file, prop1, prop2, xfactor=1, yfactor=1, rcParams=None, **kwargs
):
    """Function to plot a property vs. a property.

    Args:
        ``files`` (:obj:`str`): A string giving the xml file.

        ``prop1`` (:obj:`str`): A string giving the property (which will be
        the abscissa of the plot).

        ``prop2`` (:obj:`str`): A string giving the property (which will be
        the ordinate of the plot).

        ``xfactor`` (:obj:`float`, optional): A float giving the scaling for
        the abscissa values.  Defaults to 1.

        ``yfactor`` (:obj:`float`, optional): A float giving the scaling for
        the ordinate values.  Defaults to 1.

        ``rcParams`` (:obj:`dict`, optional): A dictionary of
        :obj:`matplotlib.rcParams` to be applied to the plot.
        Defaults to leaving the current rcParams unchanged.

        ``**kwargs``:  Acceptable :obj:`matplotlib.pyplot` functions.  Include
        directly, as a :obj:`dict`, or both.

    Returns:
        A matplotlib plot.

    Example:

        >>> import wnutils.plot.xml as wp
        >>> kw = {'xlabel': 'time (yr)'}
        >>> wp.plot_property_vs_property(
        ...     'my_output.xml',
        ...     'time',
        ...     't9',
        ...     xfactor = 3.15e7,
        ...     rcParams = {'lines.linewidth': 3},
        ...     ylim = [0,10],
        ...     **kw
        ... )
        ...

    """

    plp.set_plot_params(mpl, rcParams)

    result = wx.get_properties_in_zones_as_floats(file, [prop1, prop2])

    plp.apply_class_methods(plt, kwargs)

    plt.plot(result[prop1] / xfactor, result[prop2] / yfactor)

    if('xlabel' not in kwargs):
        plt.xlabel(prop1)

    if('ylabel' not in kwargs):
        plt.ylabel(prop2)

    plt.show()


def plot_zone_abundances_vs_nucleon_number(
    file, nucleon, zone_xpath, rcParams=None, **kwargs
):
    """Function to plot abundances summed by nucleon number.

    Args:
        ``files`` (:obj:`str`): A string giving the xml file.

        ``nucleon`` (:obj:`str`): A string giving the nucleon (must be 'z',
        'n', or 'a').

        ``zone_xpath`` (:obj:`str`): A string giving the XPath expression to
        select the (single) zone.

        ``rcParams`` (:obj:`dict`, optional): A dictionary of
        :obj:`matplotlib.rcParams` to be applied to the plot.
        Defaults to leaving the current rcParams unchanged.

        ``**kwargs``:  Acceptable :obj:`matplotlib.pyplot` functions.  Include
        directly, as a :obj:`dict`, or both.

    Returns:
        A matplotlib plot.

    Example:

        >>> import wnutils.plot.xml as wp
        >>> wp.plot_zone_abundances_vs_nucleon_number(
        ...     'my_output.xml',
        ...     'z',
        ...     '[last()]',
        ...     rcParams = {'lines.linewidth': 3},
        ...     yscale = 'log', xlabel = 'Z', ylabel = 'Elemental Abundance',
        ...     ylim = [1.e-10,1]
        ... )
        ...

    """

    plp.set_plot_params(mpl, rcParams)

    y = (
        wx.get_abundances_vs_nucleon_number_in_zones(
            file, nucleon, zone_xpath
        )
    )

    plp.apply_class_methods(plt, kwargs)

    plt.plot(y[0, :])
    plt.show()
