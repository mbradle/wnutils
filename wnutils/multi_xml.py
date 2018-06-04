import wnutils.base as wb
import wnutils.xml as wx
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np


class Multi_Xml(wb.Base):
    """A class for reading and plotting webnucleo multiple xml files.

       Each instance corresponds to a set of xml files.  Methods
       plot data from the files.

       Args:
           ``files`` (:obj:`list`): The names of the xml files.

       """

    def __init__(self, files):
        self._files = files
        self._xml = []
        for file in files:
            self._xml.append(wx.Xml(file))

    def get_files(self):
        """Method to return the names of the input files.

        Returns:
            :obj:`list`:  A list of :obj:`str` giving the files

        """
        return self._files

    def get_xml(self):
        """Method to return individual Xml instances.

        Returns:
            :obj:`list`:  A list of individual wnutils.xml.Xml instances.

        """
        return self._xml

    def plot_property_vs_property(
        self, prop1, prop2, xfactor=1, yfactor=1, rcParams=None,
        labels=None, **kwargs
    ):
        """Method to plot a property vs. a property in the files.

        Args:

            ``prop1`` (:obj:`str`): A string giving the property(which will
            be the abscissa of the plot).

            ``prop2`` (:obj:`str`): A string giving the property(which will
            be the ordinate of the plot).

            ``xfactor`` (:obj:`float`, optional): A float giving the scaling
            for the abscissa values.  Defaults to 1.

            ``yfactor`` (:obj:`float`, optional): A float giving the scaling
            for the ordinate values.  Defaults to 1.

            ``rcParams`` (:obj:`dict`, optional): A dictionary of
            : obj: `matplotlib.rcParams` to be applied to the plot.
            Defaults to leaving the current rcParams unchanged.

            ``labels`` (:obj:`list`, optional): A list of strings giving
            the legend labels.

            ``**kwargs``:  Acceptable: obj: `matplotlib.pyplot` functions.
            Include directly, as a :obj:`dict`, or both.

        Returns:
            A matplotlib plot.

        """

        self.set_plot_params(mpl, rcParams)

        xmls = self.get_xml()

        if labels:
            if len(xmls) != len(labels):
                print('Number of legend labels must equal number of plots.')
                return

        for i in range(len(xmls)):
            result = xmls[i].get_properties_as_floats([prop1, prop2])
            x = result[prop1] / xfactor
            y = result[prop2] / yfactor
            if labels:
                plt.plot(x, y, label=labels[i])
            else:
                plt.plot(x, y)

        self.apply_class_methods(plt, kwargs)

        if('xlabel' not in kwargs):
            plt.xlabel(prop1)

        if('ylabel' not in kwargs):
            plt.ylabel(prop2)

        if labels and 'legend' not in kwargs:
            plt.legend()

        plt.show()

    def plot_mass_fraction_vs_property(self, prop, species, xfactor=1,
                                       use_latex_names=False, labels=None,
                                       rcParams=None, **kwargs
                                       ):
        """Method to plot a mass fraction versus a property.

        Args:

            ``prop`` (:obj:`str`): A string giving the property(which will
            be the abscissa of the plot).

            ``species`` (:obj:`str`):  A string giving the species.

            ``xfactor`` (:obj:`float`, optional): A float giving the scaling
            for the abscissa values.  Defaults to 1.

            ``use_latex_names`` (:obj:`bool`, optional): If set to True,
            converts species labels to latex format.

            ``rcParams`` (:obj:`dict`, optional): A dictionary of
            :obj:`matplotlib.rcParams` to be applied to the plot.
            Defaults to leaving the current rcParams unchanged.

            ``**kwargs``:  Acceptable :obj:`matplotlib.pyplot` functions.
            Include directly, as a :obj:`dict`, or both.

        Returns:

            A matplotlib plot.

        """

        self.set_plot_params(mpl, rcParams)

        if use_latex_names:
            latex_names = self.get_latex_names([species])

        xmls = self.get_xml()

        if labels:
            if len(xmls) != len(labels):
                print('Number of legend labels must equal number of plots.')
                return

        for xml in xmls:
            x = xml.get_properties_as_floats([prop])[prop] / xfactor
            y = xml.get_mass_fractions([species])
            if labels:
                plt.plot(x, y[species], label=labels[i])
            else:
                plt.plot(x, y[species])

        self.apply_class_methods(plt, kwargs)

        if('xlabel' not in kwargs):
            plt.xlabel(prop)

        if('ylabel' not in kwargs):
            if use_latex_names:
                s = '$X(' + latex_names[species[0]][1:-1] + ')$'
            else:
                s = species[0]
            plt.ylabel(s)

        if labels and 'legend' not in kwargs:
            plt.legend()

        plt.show()
