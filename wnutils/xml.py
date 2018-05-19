import wnutils.wnbase as wb
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from lxml import etree


class Xml(wb.WnBase):
    """A class for reading and plotting webnucleo xml files.

       Each instance corresponds to an xml file.  Methods extract
       data and plot data from the file.

       Args:
           ``file`` (:obj:`str`): The name of the xml file.

       """

    def __init__(self, file):
        self._root = etree.parse(file).getroot()

    def _get_species_data(self):
        result = []

        species = self._root.xpath('//nuclear_data/nuclide')

        for sp in species:
            data = {}
            data['z'] = (sp.xpath('z'))[0].text
            data['a'] = (sp.xpath('a'))[0].text
            result.append(data)

        return result

    def _get_species_data_for_zone(self, zone):
        result = {}

        species = zone.xpath('mass_fractions/nuclide')

        for sp in species:
            data = {}
            data['z'] = int((sp.xpath('z'))[0].text)
            data['a'] = int((sp.xpath('a'))[0].text)
            data['n'] = data['a'] - data['z']
            data['x'] = float((sp.xpath('x'))[0].text)
            result[sp.xpath('@name')[0]] = data

        return result

    def _get_zones(self, zone_xpath):
        return self._root.xpath('//zone' + zone_xpath)

    def get_mass_fractions(self, species, zone_xpath=' '):
        """Method to retrieve mass fractions of species in specified zones.

        Args:
            ``species`` (:obj:`list`): List of strings giving requested
            species.

            ``zone_xpath`` (:obj:`str`, optional): XPath expression to select
            zones.  Defaults to all zones.

        Returns:
            :obj:`dict`: A dictionary of :obj:`numpy.array` containing the
            mass fractions of the requested species in the zones as floats.

        """

        dict = {}

        for my_species in species:
            dict[my_species] = []

        zones = self._get_zones(zone_xpath)

        for zone in zones:

            for my_species in species:

                data = zone.find(
                    'mass_fractions/nuclide[@name="%s"]/x' % my_species)

                if data is None:
                    dict[my_species].append(0.)
                else:
                    dict[my_species].append(data.text)

        result = {}

        for my_species in species:
            result[my_species] = np.array(dict[my_species], np.float_)

        return result

    def get_properties(self, properties, zone_xpath=' '):
        """Method to retrieve properties in specified zones in an xml file

        Args:
            ``properties`` (:obj:`list`): List of strings giving requested
            properites.

            ``zone_xpath`` (:obj:`str`, optional): XPath expression to select
            zones.  Defaults to all zones.

        Returns:
            :obj:`dict`: A dictionary of lists containing the properties in
            the zones as strings.

        """

        properties_t = {}

        for property in properties:
            if property.isalnum():
                properties_t[property] = (property,)
            else:
                properties_t[property] = (property.split(","))
                if len(properties_t[property]) > 3:
                    print("\nToo many property tags (at most 2)!\n")
                    exit()

        dict = {}

        for property in properties:
            dict[property] = []

        for property in properties:

            tup = properties_t[property]

            path = '//zone' + zone_xpath + '/optional_properties/property'

            if len(tup) == 1:
                path += '[@name="%s"]' % tup[0].strip()
            elif len(tup) == 2:
                path += '[@name="%s" and @tag1="%s"]' % (
                    tup[0].strip(), tup[1].strip())
            else:
                path += '[@name="%s" and @tag1="%s" and @tag2="%s"]' % (
                    tup[0].strip(), tup[1].strip(), tup[2].strip())

            props = self._root.xpath(path)

            if len(props) == 0:
                print("Property not found.")
                return

            for elem in props:
                dict[property].append(elem.text)

        return dict

    def get_properties_as_floats(self, properties, zone_xpath=' '):
        """Method to retrieve properties in zones in an xml file as floats.

        Args:
            ``properties`` (:obj:`list`): List of strings giving requested
            properites.

            ``zone_xpath`` (:obj:`str`, optional): XPath expression to select
            zones.  Defaults to all zones.

        Returns:
            :obj:`dict`: A dictionary of :obj:`numpy.array` containing the
            properties in the zones as floats.

        """


        props = self.get_properties(properties)

        for prop in props:
            props[prop] = np.array(props[prop], np.float_)

        return props

    def get_abundances_vs_nucleon_number( self, nucleon='a', zone_xpath=' ' ):
        """Method to retrieve abundances summed over nucleon number in zones.

        Args:
            ``nucleon`` (:obj:`str`): String giving the nucleon number to sum
            over.  Must be 'z', 'n', or 'a'.  Defaults to 'a'.

            ``zone_xpath`` (:obj:`str`, optional): XPath expression to select
            zones.  Defaults to all zones.

        Returns:
            :obj:`numpy.array`: A two-dimensional array in which the first
            index gives the zone and the second gives the nucleon number
            value.

        """

        if(nucleon != 'z' and nucleon != 'n' and nucleon != 'a'):
            print("nucleon must be 'z', 'n', or 'a'.")
            return

        zones = self._get_zones(zone_xpath)

        result = np.array([])

        for zone in zones:
            sp = self._get_species_data_for_zone(zone)

            n = []

            for s in sp:
                n.append(sp[s][nucleon])

            y = [0.] * (max(n) + 1)

            for s in sp:
                y[sp[s][nucleon]] += sp[s]['x'] / sp[s]['a']

            if(result.size == 0):
                result = np.append(result, y)
            else:
                result = np.vstack([result, y])

        return result

    def plot_property_vs_property(
        self, prop1, prop2, xfactor=1, yfactor=1, rcParams=None, **kwargs
    ):
        """Method to plot a property vs. a property.

        Args:

            ``prop1`` (:obj:`str`): A string giving the property (which will
            be the abscissa of the plot).

            ``prop2`` (:obj:`str`): A string giving the property (which will
            be the ordinate of the plot).

            ``xfactor`` (:obj:`float`, optional): A float giving the scaling
            for the abscissa values.  Defaults to 1.

            ``yfactor`` (:obj:`float`, optional): A float giving the scaling
            for the ordinate values.  Defaults to 1.

            ``rcParams`` (:obj:`dict`, optional): A dictionary of
            :obj:`matplotlib.rcParams` to be applied to the plot.
            Defaults to leaving the current rcParams unchanged.

            ``**kwargs``:  Acceptable :obj:`matplotlib.pyplot` functions.
            Include directly, as a :obj:`dict`, or both.

        Returns:
            A matplotlib plot.

        """

        self.set_plot_params(mpl, rcParams)

        result = self.get_properties_as_floats([prop1, prop2])

        self.apply_class_methods(plt, kwargs)

        plt.plot(result[prop1] / xfactor, result[prop2] / yfactor)

        if('xlabel' not in kwargs):
            plt.xlabel(prop1)

        if('ylabel' not in kwargs):
            plt.ylabel(prop2)

        plt.show()

    def plot_mass_fractions_vs_property(self, prop, species, xfactor=1):
        """Method to plot the mass fractions versus a property.

        Args:

            ``prop`` (:obj:`str`): A string giving the property (which will
            be the abscissa of the plot).

            ``species``:obj:`list`):  A list of strings giving the species.

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

        fig = plt.figure()

        y = []
        l = []
        latex_names = []

        x = self.get_properties_as_floats([prop])[prop] / xfactor

        y = self.get_mass_fractions(species)

        for i in range(len(species)):
            lab = species[i]
            l.append(plt.plot(x, y[species[i]], label=lab))

        plt.legend()

        plt.show()

    def plot_abundances_vs_nucleon_number(
        self, nucleon, zone_xpath, rcParams=None, **kwargs
    ):
        """Method to plot abundances summed by nucleon number.

        Args:

            ``nucleon`` (:obj:`str`): A string giving the nucleon (must be
            'z', 'n', or 'a').

            ``zone_xpath`` (:obj:`str`): A string giving the XPath expression
            to select the (single) zone.

            ``rcParams`` (:obj:`dict`, optional): A dictionary of
            :obj:`matplotlib.rcParams` to be applied to the plot.
            Defaults to leaving the current rcParams unchanged.

            ``**kwargs``:  Acceptable :obj:`matplotlib.pyplot` functions.
            Include directly, as a :obj:`dict`, or both.

        Returns:
            A matplotlib plot.

        """


        self.set_plot_params(mpl, rcParams)

        y = (
            self.get_abundances_vs_nucleon_number(nucleon, zone_xpath)
        )

        self.apply_class_methods(plt, kwargs)

        if len(y.shape) != 1:
            print("Include only one zone in XPath.")
            return

        plt.plot(y)

        plt.show()
