import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

import wnutils.read.xml as wx
import wnutils.params as plp
import wnutils.utils as wu


def plot_mass_fraction_vs_property_in_files(
    files, prop, species, legend_labels = None, **kwargs
):

    plp.set_plot_params(plt, kwargs)

    if legend_labels:
        if(len(legend_labels) != len(files)):
            print("Invalid legend labels for input files.")
            return

    fig = plt.figure()

    for i in range(len(files)):
        x = (wx.get_properties_in_zones_as_floats(files[i], [prop]))[prop]
        if('xfactor' in kwargs):
            x /= float(kwargs['xfactor'])
        y = wx.get_mass_fractions_in_zones(files[i], [species])[species]
        if legend_labels:
            ll, = plt.plot(x, y, label=legend_labels[i])
        else:
            ll, = plt.plot(x, y)

    plp.apply_class_methods(plt, kwargs)

    if('use_latex_names' in kwargs):
        if(kwargs['use_latex_names'] == 'yes'):
            plt.ylabel(
                'X(' + wu.get_latex_names([species])[species] + ')'
            )

    if legend_labels:
        plt.legend()

    plt.show()


def plot_mass_fractions(
    file, species, **kwargs
):

    plp.set_plot_params(mpl, kwargs)

    fig = plt.figure()

    y = []
    l = []
    latex_names = []

    y = wx.get_mass_fractions_in_zones(file, species)

    if('use_latex_names' in kwargs):
        if(kwargs['use_latex_names'] == 'yes'):
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
    file, prop, species, **kwargs
):

    plp.set_plot_params(mpl, kwargs)

    fig = plt.figure()

    y = []
    l = []
    latex_names = []

    x = (wx.get_properties_in_zones_as_floats(file, [prop]))[prop]
    if('xfactor' in kwargs):
        x /= float(kwargs['xfactor'])

    y = wx.get_mass_fractions_in_zones(file, species)

    if('use_latex_names' in kwargs):
        if(kwargs['use_latex_names'] == 'yes'):
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


def plot_property(
    file, prop, **kwargs
):

    plp.set_plot_params(mpl, kwargs)

    x = (wx.get_properties_in_zones_as_floats(file, [prop]))[prop]
    if('xfactor' in kwargs):
        x /= float(kwargs['xfactor'])

    plp.apply_class_methods(plt, kwargs)

    plt.plot(x)
    plt.show()


def plot_property_vs_property(
    file, prop1, prop2, **kwargs
):

    plp.set_plot_params(mpl, kwargs)

    result = wx.get_properties_in_zones_as_floats(file, [prop1, prop2])

    x = result[prop1]
    if('xfactor' in kwargs):
        x /= float(kwargs['xfactor'])

    y = result[prop2]
    if('yfactor' in kwargs):
        y /= float(kwargs['yfactor'])

    plp.apply_class_methods(plt, kwargs)

    plt.plot(x,y)
    plt.show()


def plot_zone_abundances_vs_nucleon_number(
    file, nucleon, zone_xpath, **kwargs
):

    y = (
        wx.get_abundances_vs_nucleon_number_in_zones(
            file, nucleon, zone_xpath
        )
    )

    plp.apply_class_methods(plt, kwargs)

    plt.plot(y[0])
    plt.show()
