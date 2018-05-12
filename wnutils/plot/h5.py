import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

import wnutils.read.h5 as w5
import wnutils.params as plp
import wnutils.utils as wu


def plot_zone_property_vs_property(
    file, zone, prop1, prop2, **kwargs
):

    result = (
        w5.get_zone_properties_in_groups_as_floats(file, zone, [prop1, prop2])
    )

    if('xfactor' in kwargs):
        result[prop1] /= xfactor

    plp.apply_class_methods(plt, kwargs)

    plt.plot(result[prop1], result[prop2])
    plt.show()


def plot_group_mass_fractions(
    file, group, species, **kwargs
):

    plp.set_plot_params(mpl, kwargs)

    fig = plt.figure()

    y = []
    l = []
    latex_names = []

    m = w5.get_group_mass_fractions(file, group)

    nuclide_data = w5.get_nuclide_data_hash(file)

    if('use_latex_names' in kwargs):
        if(kwargs['use_latex_names'] == 'yes'):
            laxtex_names = wu.get_latex_names(species)

    iy = 0
    for sp in species:
        y = np.array(map(float, m[:, nuclide_data[sp]['index']]))
        if(len(latex_names) != 0):
            lab = latex_names[sp]
        else:
            lab = sp
        l.append(plt.plot(y, label=lab))

    if(len(species) != 1):
        plt.legend(loc='upper right', prop={'size': 14})

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
    file, group, prop, species, **kwargs
):

    plp.set_plot_params(mpl, kwargs)

    fig = plt.figure()

    y = []
    l = []
    latex_names = []

    x = w5.get_group_properties_in_zones(file, group, [prop])
    m = w5.get_group_mass_fractions(file, group)

    nuclide_data = w5.get_nuclide_data_hash(file)

    if('xfactor' in kwargs):
        x /= kwargs['xfactor']

    if('use_latex_names' in kwargs):
        if(kwargs['use_latex_names'] == 'yes'):
            laxtex_names = wu.get_latex_names(species)

    iy = 0
    for sp in species:
        y = np.array(map(float, m[:, nuclide_data[sp]['index']]))
        if(len(latex_names) != 0):
            lab = latex_names[sp]
        else:
            lab = sp
        l.append(plt.plot(x, y, label=lab))

    if(len(species) != 1):
        plt.legend(loc='upper right', prop={'size': 14})

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
    file, zone, prop, species, **kwargs
):

    plp.set_plot_params(mpl, kwargs)

    fig = plt.figure()

    x = []
    y = []
    l = []
    latex_names = []

    x = w5.get_zone_properties_in_groups_as_floats(file, zone, [prop])
    m = w5.get_zone_mass_fractions_in_groups(file, zone, species)

    if('xfactor' in kwargs):
        x /= kwargs['xfactor']

    if('use_latex_names' in kwargs):
        if(kwargs['use_latex_names'] == 'yes'):
            latex_names = wu.get_latex_names(species)

    for i in range(len(species)):
        y = np.array(list(map(float, m[species[i]])))
        if(len(latex_names) != 0):
            lab = latex_names[species[i]]
        else:
            lab = species[i]
        l.append(plt.plot(x, y, label=lab))

    if(len(species) != 1):
        plt.legend(loc='upper left', prop={'size': 14})

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
