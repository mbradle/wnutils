import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

import wnutils.read.xml as wx
import wnutils.params as plp
import wnutils.utils as wu


def plot_single_mass_fraction_vs_property_in_files(
    files, prop, species, **keyword_parameters
):

    plp.set_plot_params(plt, keyword_parameters)

    if('legend_labels' in keyword_parameters):
        if(len(keyword_parameters['legend_labels']) != len(files)):
            print("Invalid legend labels for input files.")
            exit(1)

    fig = plt.figure()

    y = []
    l = []

    for i in range(len(files)):
        x = (wx.get_properties_in_zones_as_floats(files[i], [prop]))[prop]
        if('xfactor' in keyword_parameters):
            x /= float(keyword_parameters['xfactor'])
        y = wx.get_mass_fractions_in_zones(files[i], [species])
        if('legend_labels' in keyword_parameters):
            ll, = plt.plot(x, y, label=keyword_parameters['legend_labels'][i])
        else:
            ll, = plt.plot(x, y)
        l.append(ll)

    plp.apply_class_methods(plt, keyword_parameters)

    if('use_latex_names' in keyword_parameters):
        if(keyword_parameters['use_latex_names'] == 'yes'):
            plt.ylabel(
                'X(' + wu.get_latex_names([species])[species] + ')'
            )

    plt.show()


def plot_mass_fractions(
    file, species, **keyword_parameters
):

    plp.set_plot_params(mpl, keyword_parameters)

    fig = plt.figure()

    y = []
    l = []
    latex_names = []

    y = wx.get_mass_fractions_in_zones(file, species)

    if('use_latex_names' in keyword_parameters):
        if(keyword_parameters['use_latex_names'] == 'yes'):
            latex_names = wu.get_latex_names(species)

    for i in range(len(species)):
        if(len(latex_names) != 0):
            lab = latex_names[species[i]]
        else:
            lab = species[i]
        l.append(plt.plot(y[species[i]], label=lab))

    if('ylabel' not in keyword_parameters):
        if(len(species) != 1):
            plt.ylabel('Mass Fraction')
        else:
            if(len(latex_names) == 0):
                plt.ylabel('X(' + species[0] + ')')
            else:
                plt.ylabel('X(' + latex_names[species[0]] + ')')

    if('xlabel' not in keyword_parameters):
        plt.xlabel('step')

    plp.apply_class_methods(plt, keyword_parameters)

    plt.show()


def plot_mass_fractions_vs_property(
    file, prop, species, **keyword_parameters
):

    plp.set_plot_params(mpl, keyword_parameters)

    fig = plt.figure()

    y = []
    l = []
    latex_names = []

    x = (wx.get_properties_in_zones_as_floats(file, [prop]))[prop]
    if('xfactor' in keyword_parameters):
        x /= float(keyword_parameters['xfactor'])

    y = wx.get_mass_fractions_in_zones(file, species)

    if('use_latex_names' in keyword_parameters):
        if(keyword_parameters['use_latex_names'] == 'yes'):
            latex_names = wu.get_latex_names(species)

    for i in range(len(species)):
        if(len(latex_names) != 0):
            lab = latex_names[species[i]]
        else:
            lab = species[i]
        l.append(plt.plot(x, y[species[i]], label=lab))

    if('ylabel' not in keyword_parameters):
        if(len(species) != 1):
            plt.ylabel('Mass Fraction')
        else:
            if(len(latex_names) == 0):
                plt.ylabel('X(' + species[0] + ')')
            else:
                plt.ylabel('X(' + latex_names[species[0]] + ')')

    if len(species) != 1:
        plt.legend()

    if('xlabel' not in keyword_parameters):
        plt.xlabel(prop)

    plp.apply_class_methods(plt, keyword_parameters)

    plt.show()


def plot_property(
    file, prop, **keyword_parameters
):

    plp.set_plot_params(mpl, keyword_parameters)

    x = (wx.get_properties_in_zones_as_floats(file, [prop]))[prop]
    if('xfactor' in keyword_parameters):
        x /= float(keyword_parameters['xfactor'])

    plp.apply_class_methods(plt, keyword_parameters)

    plt.plot(x)
    plt.show()


def plot_property_vs_property(
    file, prop1, prop2, **keyword_parameters
):

    plp.set_plot_params(mpl, keyword_parameters)

    result = wx.get_properties_in_zones_as_floats(file, [prop1, prop2])

    x = result[prop1]
    if('xfactor' in keyword_parameters):
        x /= float(keyword_parameters['xfactor'])

    y = result[prop2]
    if('yfactor' in keyword_parameters):
        y /= float(keyword_parameters['yfactor'])

    plp.apply_class_methods(plt, keyword_parameters)

    plt.plot(x,y)
    plt.show()


def plot_zone_abundances_vs_nucleon_number(
    file, nucleon, zone_xpath, **keyword_parameters
):

    y = (
        wx.get_abundances_vs_nucleon_number_in_zones(
            file, nucleon, zone_xpath
        )
    )

    plp.apply_class_methods(plt, keyword_parameters)

    plt.plot(y[0])
    plt.show()
