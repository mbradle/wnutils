import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

import wnutils.read.h5 as w5
import wnutils.params as plp
import wnutils.utils as wu


def plot_zone_property_vs_property(
    file, zone, prop1, prop2, xfactor=1, yfactor=1, rcParams=None, **kwargs
):
    """Function to plot a property vs. a property in a zone.

    Args:
        ``file`` (:obj:`str`): A string giving the hdf5 file.

        ``zone`` (:obj:`tuple`): A three element tuple giving the zone labels.

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

        >>> import wnutils.plot.h5 as w5
        >>> kw = {'xlabel': 'time (yr)'}
        >>> w5.plot_zone_property_vs_property(
        ...     'my_output.h5', ('2','1','0'), 'time',
        ...     't9', xfactor = 3.15e7,
        ...     rcParams = {'lines.linewidth': 3},
        ...     ylim = [0,10],
        ...     **kw
        ... )
        ...

    """

    plp.set_plot_params(mpl, rcParams)

    result = (
        w5.get_zone_properties_in_groups_as_floats(file, zone, [prop1, prop2])
    )

    plp.apply_class_methods(plt, kwargs)

    plt.plot(result[prop1] / xfactor, result[prop2] / yfactor)
    plt.show()


def plot_group_mass_fractions(
    file, group, species, use_latex_names=False, rcParams=None, **kwargs
):
    """Function to plot group mass fractions vs. zone.

    Args:
        ``file`` (:obj:`str`): A string giving the hdf5 file.

        ``group`` (:obj:`str`): A string giving the group.

        ``species`` (:obj:`list`): A list of strings giving the species to
        plot.

        ``use_latex_names`` (:obj:`bool`, optional): If set to True, species
        names converted to latex format.

        ``rcParams``` (:obj:`dict`, optional): A dictionary of
        :obj:`matplotlib.rcParams` to be applied to the plot.
        Defaults to leaving the current rcParams unchanged.

        ``**kwargs``:  Acceptable :obj:`matplotlib.pyplot` functions.  Include
        directly, as a :obj:`dict`, or both.

    Returns:
        A matplotlib plot.

    Example:

        >>> import wnutils.plot.h5 as w5
        >>> w5.plot_group_mass_fractions(
        ...     'my_output.h5',
        ...     'Step 00040',
        ...     ['h1', 'he4', 'c12'],
        ...     rcParams = {'lines.linewidth': 3},
        ...     ylim = [0,1]
        ... )
        ...

    """

    plp.set_plot_params(mpl, rcParams)

    fig = plt.figure()

    l = []
    latex_names = []

    m = w5.get_group_mass_fractions(file, group)

    nuclide_data = w5.get_nuclide_data_hash(file)

    if use_latex_names:
        laxtex_names = wu.get_latex_names(species)

    iy = 0
    for sp in species:
        if(len(latex_names) != 0):
            lab = latex_names[sp]
        else:
            lab = sp
        l.append(plt.plot(m[:, nuclide_data[sp]['index']], label=lab))

    if(len(species) != 1):
        plt.legend()

    if('ylabel' not in kwargs):
        if(len(species) != 1):
            plt.ylabel('Mass Fraction')
        else:
            if(len(latex_names) == 0):
                plt.ylabel('X(' + species[0] + ')')
            else:
                plt.ylabel('X(' + latex_names[species[0]] + ')')

    plp.apply_class_methods(plt, kwargs)

    plt.show()


def plot_group_mass_fractions_vs_property(
    file, group, prop, species, xfactor=1, use_latex_names=False,
    rcParams=None, **kwargs
):
    """Function to plot group mass fractions vs. zone property.

    Args:
        ``file`` (:obj:`str`): A string giving the hdf5 file.

        ``group`` (:obj:`str`): A string giving the group.

        ``prop`` (:obj:`str`): A string giving the property (which will serve
        as the plot abscissa).

        ``species`` (:obj:`list`): A list of strings giving the species to
        plot.

        ``xfactor`` (:obj:`float`, optional): A float giving the scaling for
        the abscissa values.  Defaults to 1.

        ``use_latex_names`` (:obj:`bool`, optional): If set to True, species
        names converted to latex format.

        ``rcParams``` (:obj:`dict`, optional): A dictionary of
        :obj:`matplotlib.rcParams` to be applied to the plot.
        Defaults to leaving the current rcParams unchanged.

        ``**kwargs``:  Acceptable :obj:`matplotlib.pyplot` functions.  Include
        directly, as a :obj:`dict`, or both.

    Returns:
        A matplotlib plot.

    Example:

        >>> import wnutils.plot.h5 as w5
        >>> w5.plot_group_mass_fractions_vs_property(
        ...     'my_output.h5',
        ...     'Step 00040',
        ...     'zone mass',
        ...     ['h1', 'he4', 'c12'],
        ...    rcParams = {'lines.linewidth': 3},
        ...     ylim = [0,1]
        ... )
        ...

    """

    plp.set_plot_params(mpl, rcParams)

    fig = plt.figure()

    l = []
    latex_names = []

    x = w5.get_group_properties_in_zones_as_floats(file, group, [prop])[prop]
    m = w5.get_group_mass_fractions(file, group)

    nuclide_data = w5.get_nuclide_data_hash(file)

    if use_latex_names:
        laxtex_names = wu.get_latex_names(species)

    iy = 0
    for sp in species:
        y = m[:, nuclide_data[sp]['index']]
        if(len(latex_names) != 0):
            lab = latex_names[sp]
        else:
            lab = sp
        l.append(plt.plot(x / xfactor, y, label=lab))

    if(len(species) != 1):
        plt.legend()

    if('ylabel' not in kwargs):
        if(len(species) != 1):
            plt.ylabel('Mass Fraction')
        else:
            if(len(latex_names) == 0):
                plt.ylabel('X(' + species[0] + ')')
            else:
                plt.ylabel('X(' + latex_names[species[0]] + ')')

    if('xlabel' not in kwargs):
        plt.xlabel(prop)

    plp.apply_class_methods(plt, kwargs)

    plt.show()


def plot_zone_mass_fractions_vs_property(
    file, zone, prop, species, xfactor=1, yfactor=None,
    use_latex_names=False, rcParams=None, **kwargs
):
    """Function to plot zone mass fractions vs. zone property.

    Args:
        ``file`` (:obj:`str`): A string giving the hdf5 file.

        ``zone`` (:obj:`tuple`): A three element tuple giving the zone.

        ``prop`` (:obj:`str`): A string giving the property (which will serve
        as the plot abscissa).

        ``species`` (:obj:`list`): A list of strings giving the species to
        plot.

        ``xfactor`` (:obj:`float`, optional): A float giving the scaling for
        the abscissa values.  Defaults to 1.

        ``yfactor`` (:obj:`list`, optional): A list of floats giving factor
        by which to scale the mass fractions.  Defaults to not scaling.
        If supplied, must by the same length as ``species``.

        ``use_latex_names`` (:obj:`bool`, optional): If set to True, species
        names converted to latex format.

        ``rcParams`` (:obj:`dict`, optional): A dictionary of
        :obj:`matplotlib.rcParams` to be applied to the plot.
        Defaults to leaving the current rcParams unchanged.

        ``**kwargs``:  Acceptable :obj:`matplotlib.pyplot` functions.  Include
        directly, as a :obj:`dict`, or both.

    Returns:
        A matplotlib plot.

    Example:

        >>> import wnutils.plot.h5 as w5
        >>> kw = {'xlabel': 'time (s)', 'xscale': 'log'}
        >>> w5.plot_zone_mass_fractions_vs_property(
        ...     'my_output.h5',
        ...     ('1', '0', '0'),
        ...     'time',
        ...     ['h1', 'he4', 'c12'],
        ...     rcParams = {'lines.linewidth': 3},
        ...     ylim = [0,1]
        ...     **kw
        ... )
        ...

    """

    plp.set_plot_params(mpl, rcParams)

    fig = plt.figure()

    l = []
    latex_names = []

    x = w5.get_zone_properties_in_groups_as_floats(file, zone, [prop])[prop]
    m = w5.get_zone_mass_fractions_in_groups(file, zone, species)

    if yfactor:
        if len(yfactor) != len(species):
            print('yfactor length must be the same as the number of species.')
            return
    else:
        yfactor = np.full(len(species), 1.)

    if use_latex_names:
        latex_names = wu.get_latex_names(species)

    for i in range(len(species)):
        if(len(latex_names) != 0):
            lab = latex_names[species[i]]
        else:
            lab = species[i]
        l.append(plt.plot(x / xfactor, m[species[i]] / yfactor[i], label=lab))

    if(len(species) != 1):
        plt.legend()

    if('ylabel' not in kwargs):
        if(len(species) != 1):
            plt.ylabel('Mass Fraction')
        else:
            if(len(latex_names) == 0):
                plt.ylabel('X(' + species[0] + ')')
            else:
                plt.ylabel('X(' + latex_names[species[0]] + ')')

    if('xlabel' not in kwargs):
        plt.xlabel(prop)

    plp.apply_class_methods(plt, kwargs)

    plt.show()
