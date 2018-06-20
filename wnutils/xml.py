import wnutils.base as wb
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from lxml import etree


class Xml(wb.Base):
    """A class for reading and plotting webnucleo xml files.

       Each instance corresponds to an xml file.  Methods extract
       data and plot data from the file.

       Args:
           ``file`` (:obj:`str`): The name of the xml file.

       """

    def __init__(self, file):
        self._root = etree.parse(file).getroot()

    def _get_nuclide_data_array(self, nuc_xpath):
        result = []

        nuclides = self._root.xpath('//nuclear_data/nuclide' + nuc_xpath)

        for nuc in nuclides:
            data = {}
            data['z'] = int((nuc.xpath('z'))[0].text)
            data['a'] = int((nuc.xpath('a'))[0].text)
            data['n'] = data['a'] - data['z']
            data['source'] = (nuc.xpath('source'))[0].text
            data['spin'] = float((nuc.xpath('spin'))[0].text)
            if nuc.xpath('state'):
                data['state'] = (nuc.xpath('state'))[0].text
            else:
                data['state'] = ''
            data['mass excess'] = float((nuc.xpath('mass_excess'))[0].text)
            partf = nuc.xpath('partf_table/point')
            data['t9'] = np.zeros(len(partf))
            data['partf'] = np.zeros(len(partf))
            for i, elem in enumerate(partf):
                data['t9'][i] = float((elem.xpath('t9')[0].text).strip())
                data['partf'][i] = np.power(
                    10.,
                    float(
                        (elem.xpath('log10_partf')[0].text).strip()
                    )
                ) * (2. * data['spin'] + 1.)
            ind = data['t9'].argsort()
            data['t9'] = data['t9'][ind]
            data['partf'] = data['partf'][ind]
            result.append(data)

        return result

    def _get_max_nucleon_numbers(self):
        nd = self._get_nuclide_data_array('')

        z = np.zeros(len(nd), dtype=np.int8)
        n = np.zeros(len(nd), dtype=np.int8)
        a = np.zeros(len(nd), dtype=np.int8)

        for i in range(len(nd)):
            z[i] = nd[i]['z']
            n[i] = nd[i]['n']
            a[i] = nd[i]['a']

        return {'z': np.amax(z), 'n': np.amax(n), 'a': np.amax(a)}

    def get_nuclide_data(self, nuc_xpath=' '):
        """Method to retrieve nuclear data from webnucleo XML.

        Args:
            ``nuc_xpath`` (:obj:`str`, optional): XPath expression to select
            nuclides.  Defaults to all nuclides.

        Returns:
            :obj:`dict`: A dictionary of nuclide data.  The data for each
            nuclide are themselves contained in a :obj:`dict`.

        """
        result = {}
        nuclides = self._get_nuclide_data_array(nuc_xpath)
        for i in range(len(nuclides)):
            s = self.create_nuclide_name(
                nuclides[i]['z'], nuclides[i]['a'], nuclides[i]['state']
            )
            result[s] = nuclides[i]

        return result

    def get_network_limits(self, nuc_xpath = ' '):
        """Method to retrieve the network limits from the nuclide data.

        Args:
            ``nuc_xpath`` (:obj:`str`, optional): XPath expression to select
            the nuclides.  Defaults to all nuclides.

        Returns:
            :obj:`dict`: A dictionary of :obj:`numpy.array` containing the
            network limits.  The array with key `z` gives the atomic values.
            The array with key `n_min` gives the lowest neutron number present
            for the corresponding atomic number.  The array with key `n_max`
            gives the highest neutron number present for the corresponding
            atomic number.

        """

        nd = self._get_nuclide_data_array(nuc_xpath)

        zs = set()

        for i in range(len(nd)):
            if nd[i]['z'] not in zs:
                zs.add(nd[i]['z'])

        zt = []
        for zz in zs:
            zt.append(zz)

        zt.sort()

        zlim = [[] for i in range(len(zt))]

        for i in range(len(nd)):
            loc = [j for j, zj in enumerate(zt) if zj == nd[i]['z']]
            zlim[loc[0]].append(nd[i]['n'])
            
        z = np.zeros(len(zlim), dtype=np.int_)
        n_min = np.zeros(len(zlim), dtype=np.int_)
        n_max = np.zeros(len(zlim), dtype=np.int_)

        for i in range(len(zlim)):
            z[i] = int(zt[i])
            n_min[i] = int(min(zlim[i]))
            n_max[i] = int(max(zlim[i]))

        return {'z': z, 'n_min': n_min, 'n_max': n_max}

    def _get_nuclide_data_for_zone(self, zone):
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
        return self._root.xpath('//zone_data/zone' + zone_xpath)

    def get_mass_fractions(self, nuclides, zone_xpath=' '):
        """Method to retrieve mass fractions of nuclides in specified zones.

        Args:
            ``nuclides`` (:obj:`list`): List of strings giving the species
            to retrieve.

            ``zone_xpath`` (:obj:`str`, optional): XPath expression to select
            zones.  Defaults to all zones.

        Returns:
            :obj:`dict`: A dictionary of :obj:`numpy.array` containing the
            mass fractions of the requested nuclides in the zones as floats.

        """

        result = {}

        zones = self._get_zones(zone_xpath)

        for nuclide in nuclides:
            result[nuclide] = np.zeros(len(zones))

        for i in range(len(zones)):
            for nuclide in nuclides:
                data = zones[i].find(
                    'mass_fractions/nuclide[@name="%s"]/x' % nuclide
                )
                if data is not None:
                    result[nuclide][i] = float(data.text)

        return result

    def get_properties(self, properties, zone_xpath=' '):
        """Method to retrieve properties in specified zones in an xml file

        Args:
            ``properties`` (:obj:`list`): List of strings or tuples
            (each of up to three strings) giving requested properites.

            ``zone_xpath`` (:obj:`str`, optional): XPath expression to select
            zones.  Defaults to all zones.

        Returns:
            :obj:`dict`: A dictionary of lists containing the properties in
            the zones as strings.

        """

        properties_t = {}

        for property in properties:
            if type(property) is str:
                properties_t[property] = (property,)
            else:
                properties_t[property] = property
                if len(properties_t[property]) > 3:
                    print("\nToo many property names (at most 3)!\n")
                    return

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
                print("Property", self._get_property_name(tup), "not found.")
                return

            for elem in props:
                dict[property].append(elem.text)

        return dict

    def get_all_properties_for_zone(self, zone_xpath):
        """Method to retrieve all properties in a zone in an xml file

        Args:
            ``zone_xpath`` (:obj:`str`): XPath expression to select
            zone.  Must be evaluate to a single zone.

        Returns:
            :obj:`dict`: A dictionary containing all the properties in
            the zone as strings.

        """

        result = {}

        zones = self._get_zones(zone_xpath)

        if len(zones) != 1:
            print('Incorrect number of zones.')
            return

        props = zones[0].xpath('optional_properties/property')

        for property in props:
            p_name = ''
            name = property.xpath('@name')
            tag1 = property.xpath('@tag1')
            tag2 = property.xpath('@tag2')
            if len(tag2) == 0 and len(tag1) == 0:
                p_name = name[0]
            elif len(tag2) == 0:
                p_name = (name[0], tag1[0])
            else:
                p_name = (name[0], tag1[0], tag2[0])
            result[p_name] = property.text

        return result

    def get_properties_as_floats(self, properties, zone_xpath=' '):
        """Method to retrieve properties in zones in an xml file as floats.

        Args:
            ``properties`` (:obj:`list`): List of strings or tuples
            (each of up to three strings) giving requested properites.

            ``zone_xpath`` (:obj:`str`, optional): XPath expression to select
            zones.  Defaults to all zones.

        Returns:
            :obj:`dict`: A dictionary of :obj:`numpy.array` containing the
            properties in the zones as floats.

        """

        props = self.get_properties(properties, zone_xpath)

        for prop in props:
            props[prop] = np.array(props[prop], np.float_)

        return props

    def get_all_abundances_in_zones(self, zone_xpath=' '):
        """Method to retrieve all abundances in zones.

        Args:
            ``zone_xpath`` (:obj:`str`, optional): XPath expression to select
            zones.  Defaults to all zones.

        Returns:
            :obj:`numpy.array`: A three-dimensional array in which the first
            index gives the zone, the second gives the atomic number,
            and the third gives the neutron number.  The array value
            is the abundance.

        """

        zones = self._get_zones(zone_xpath)

        m = self._get_max_nucleon_numbers()

        result = np.zeros((len(zones), m['z'] + 1, m['n'] + 1))

        for i in range(len(zones)):
            sp = self._get_nuclide_data_for_zone(zones[i])

            for s in sp:
                result[i, sp[s]['z'], sp[s]['n']] += sp[s]['x'] / sp[s]['a']

        return result

    def get_abundances_vs_nucleon_number(self, nucleon='a', zone_xpath=' '):
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

        m = self._get_max_nucleon_numbers()

        result = np.zeros((len(zones), m[nucleon] + 1))

        for i in range(len(zones)):
            sp = self._get_nuclide_data_for_zone(zones[i])

            for s in sp:
                result[i, sp[s][nucleon]] += sp[s]['x'] / sp[s]['a']

        return result

    def plot_property_vs_property(
        self, prop1, prop2, xfactor=1, yfactor=1, rcParams=None,
        plotParams=None, **kwargs
    ):
        """Method to plot a property vs. a property.

        Args:

            ``prop1`` (:obj:`str` or :obj:`tuple`): A string or tuple
            of up to three strings giving the property (which will be the
            abscissa of the plot).

            ``prop2`` (:obj:`str` or :obj:`tuple`): A string or tuple
            of up to three strings giving the property (which will be the
            ordinate of the plot).

            ``xfactor`` (:obj:`float`, optional): A float giving the scaling
            for the abscissa values.  Defaults to 1.

            ``yfactor`` (:obj:`float`, optional): A float giving the scaling
            for the ordinate values.  Defaults to 1.

            ``rcParams`` (:obj:`dict`, optional): A dictionary of
            :obj:`matplotlib.rcParams` to be applied to the plot.
            Defaults to the default rcParams.

            ``plotParams`` (:obj:`dict`, optional): A dictionary of
            valid :obj:`matplotlib.pyplot.plot` optional keyword arguments
            to be applied to the plot.

            ``**kwargs``:  Acceptable :obj:`matplotlib.pyplot` functions.
            Include directly, as a :obj:`dict`, or both.

        Returns:
            A matplotlib plot.

        """

        self.set_plot_params(mpl, rcParams)

        result = self.get_properties_as_floats([prop1, prop2])

        self.apply_class_methods(plt, kwargs)

        x = result[prop1] / xfactor
        y = result[prop2] / yfactor

        if plotParams:
            plt.plot(x, y, **plotParams)
        else:
            plt.plot(x, y)

        if('xlabel' not in kwargs):
            plt.xlabel(prop1)

        if('ylabel' not in kwargs):
            plt.ylabel(prop2)

        plt.show()

    def plot_mass_fractions_vs_property(self, prop, species, xfactor=1,
                                        use_latex_names=False, rcParams=None,
                                        plotParams=None, **kwargs
                                        ):
        """Method to plot the mass fractions versus a property.

        Args:

            ``prop`` (:obj:`str` or :obj:`tuple`): A string or tuple
            of up to three strings giving the property (which will be the
            abscissa of the plot).

            ``species``:obj:`list`):  A list of strings giving the species.

            ``xfactor`` (:obj:`float`, optional): A float giving the scaling
            for the abscissa values.  Defaults to 1.

            ``use_latex_names`` (:obj:`bool`, optional): If set to True,
            converts species labels to latex format.

            ``rcParams`` (:obj:`dict`, optional): A dictionary of
            :obj:`matplotlib.rcParams` to be applied to the plot.
            Defaults to the default rcParams.

            ``plotParams`` (:obj:`list`, optional): A list of
            dictionaries of valid :obj:`matplotlib.pyplot.plot` optional
            keyword arguments to be applied to the plot.  The list must
            have the same number of elements as ``species``.

            ``**kwargs``:  Acceptable :obj:`matplotlib.pyplot` functions.
            Include directly, as a :obj:`dict`, or both.

        Returns:

            A matplotlib plot.

        """

        self.set_plot_params(mpl, rcParams)

        if plotParams:
            if len(plotParams) != len(species):
                print(
                    'Number of plotParam elements must equal number' +
                    ' of species.'
                )
                return

        l = []

        x = self.get_properties_as_floats([prop])[prop] / xfactor

        y = self.get_mass_fractions(species)

        if use_latex_names:
            latex_names = self.get_latex_names(species)

        for i, sp in enumerate(species):
            if plotParams is None:
                p = {}
            else:
                p = plotParams[i]
            if 'label' not in p:
                if use_latex_names:
                    p = self._merge_dicts(p, {'label': latex_names[sp]})
                else:
                    p = self._merge_dicts(p, {'label': sp})
            l.append(plt.plot(x, y[sp], **p))

        self.apply_class_methods(plt, kwargs)

        if len(species) > 1 and 'legend' not in kwargs:
            plt.legend()

        if('xlabel' not in kwargs):
            plt.xlabel(prop)

        if('ylabel' not in kwargs):
            if len(species) > 1:
                plt.ylabel('Mass Fraction')
            else:
                if use_latex_names:
                    s = '$X(' + latex_names[species[0]][1:-1] + ')$'
                else:
                    s = species[0]
                plt.ylabel(s)

        plt.show()

    def plot_abundances_vs_nucleon_number(
        self, nucleon='a', zone_xpath='[last()]', rcParams=None,
        plotParams=None, **kwargs
    ):
        """Method to plot abundances summed by nucleon number.

        Args:

            ``nucleon`` (:obj:`str`, optional): A string giving the nucleon
            (must be 'z', 'n', or 'a').  Defaults to 'a'.

            ``zone_xpath`` (:obj:`str`, optional): A string giving the XPath
            expression to select the zones. Defaults to the last
            zone.

            ``rcParams`` (:obj:`dict`, optional): A dictionary of
            :obj:`matplotlib.rcParams` to be applied to the plot.
            Defaults to the default rcParams.

            ``plotParams`` (:obj:`list`, optional): A list of
            dictionaries of valid :obj:`matplotlib.pyplot.plot` optional
            keyword arguments to be applied to the plot.  The list must
            have the same number of elements as the number as zones selected
            by the zone XPath.

            ``**kwargs``:  Acceptable :obj:`matplotlib.pyplot` functions.
            Include directly, as a :obj:`dict`, or both.

        Returns:
            A matplotlib plot.

        """

        self.set_plot_params(mpl, rcParams)

        y = (
            self.get_abundances_vs_nucleon_number(nucleon, zone_xpath)
        )

        if plotParams:
            if y.shape[0] != len(plotParams):
                print(
                    'Number of plotParam elements must equal number of plots.'
                )
                return

        for i in range(y.shape[0]):
            if plotParams:
                plt.plot(y[i, :], **plotParams[i])
            else:
                plt.plot(y[i, :])

        self.apply_class_methods(plt, kwargs)

        if('xlabel' not in kwargs):
            plt.xlabel(nucleon)

        if('ylabel' not in kwargs):
            s = 'Y(' + nucleon + ')'
            plt.ylabel(s)

        if 'legend' not in kwargs:
            if plotParams:
                if 'label' in plotParams[0]:
                    plt.legend()

        plt.show()
