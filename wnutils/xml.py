"""Module providing xml classes."""

import os
import sys
from lxml import etree
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import LogNorm
from matplotlib import animation
import numpy as np
from scipy.interpolate import interp1d
import wnutils.base as wb


def validate(file):
    """Method to validate input Webnucleo XML.

    Args:
        ``file`` (:obj:`str`): The name of the xml file to validate.

    Returns:
        An error message if invalid and nothing if valid.

    """

    parser = etree.XMLParser(remove_blank_text=True)
    _xml = etree.parse(file, parser)
    _xml.xinclude()
    _root = _xml.getroot()

    xsd_dict = {
        "nuclear_data": "libnucnet__nuc.xsd",
        "reaction_data": "libnucnet__reac.xsd",
        "nuclear_network": "libnucnet__net.xsd",
        "zone_data": "zone_data.xsd",
        "libnucnet_input": "libnucnet.xsd",
    }

    schema_file = os.path.join(
        os.path.dirname(__file__), "xsd_pub", xsd_dict[_root.tag]
    )

    xml_validator = etree.XMLSchema(file=schema_file)
    xml_validator.assertValid(_xml)


class Reaction(wb.Base):
    """A class for storing and retrieving data about reactions."""

    def __init__(self):
        self.reactants = []
        self.nuclide_reactants = []
        self.products = []
        self.nuclide_products = []
        self.source = ""
        self.data = {}

    def _compute_rate_table_rate_interpolation(self, t_9):
        _t = self.data["t9"]
        _lr = np.log10(self.data["rate"])
        sef = self.data["sef"]

        if t_9 < _t[0]:
            return np.power(10.0, _lr[0]) * sef[0]
        if t_9 > _t[len(_t) - 1]:
            return np.power(10.0, _lr[len(_t) - 1]) * sef[len(_t) - 1]

        if len(_t) <= 2:
            _f1 = interp1d(_t, _lr, kind="linear")
            _f2 = interp1d(_t, sef, kind="linear")
            return np.power(10.0, _f1(t_9)) * _f2(t_9)

        _f1 = interp1d(_t, _lr, kind="cubic")
        _f2 = interp1d(_t, sef, kind="cubic")
        return np.power(10.0, _f1(t_9)) * _f2(t_9)

    def _compute_rate_table_rate(self, t_9):
        if isinstance(t_9, float):
            return self._compute_rate_table_rate_interpolation(t_9)

        return np.array(
            [self._compute_rate_table_rate_interpolation(x) for x in t_9]
        )

    def _compute_non_smoker_fit_rate_for_fit(self, fit, t_9):
        def non_smoker_function(fit, t_9):
            x_fit = (
                fit["a1"]
                + fit["a2"] / t_9
                + fit["a3"] / np.power(t_9, 1.0 / 3.0)
                + fit["a4"] * np.power(t_9, 1.0 / 3.0)
                + fit["a5"] * t_9
                + fit["a6"] * np.power(t_9, 5.0 / 3.0)
                + fit["a7"] * np.log(t_9)
            )
            return np.exp(x_fit)

        if t_9 < fit["Tlowfit"]:
            return non_smoker_function(fit, fit["Tlowfit"])
        if t_9 > fit["Thighfit"]:
            return non_smoker_function(fit, fit["Thighfit"])

        return non_smoker_function(fit, t_9)

    def _compute_non_smoker_fit_rate(self, t_9):
        fits = self.data["fits"]

        if len(fits) != 0:
            result = 0.0
            for fit in fits:
                result += self._compute_non_smoker_fit_rate_for_fit(fit, t_9)
            return result

        return self._compute_non_smoker_fit_rate_for_fit(self.data, t_9)

    def compute_rate(self, t_9, user_funcs=" "):
        """Method to compute rate for a reaction at input t9.

        Args:
            ``t9`` (:obj:`float`):  The temperature in billions of K giving
            the rate for the reaction.

            ``user_funcs`` (:obj:`dict`, optional):  A dictionary of
            user-defined functions associated with a user_rate key.

        Returns:
            :obj:`float`: The computed rate.

        """

        if self.data["type"] == "single_rate":
            return self.data["rate"]
        if self.data["type"] == "rate_table":
            return self._compute_rate_table_rate(t_9)
        if self.data["type"] == "non_smoker_fit":
            return self._compute_non_smoker_fit_rate(t_9)
        if self.data["type"] == "user_rate":
            if self.data["key"] not in user_funcs:
                print("Function not defined for key " + self.data["key"])
                return None
            return user_funcs[self.data["key"]](self, t_9)

        print("No such reaction type")
        return None

    def _get_reactant_and_product_xpath(self):
        reactants = []
        for _r in self.reactants:
            reactants.append(_r)
        products = []
        for _p in self.products:
            products.append(_p)
        result = "[reactant = '" + reactants[0] + "'"
        for i in range(1, len(reactants)):
            result += " and reactant = '" + reactants[i] + "'"
        for _p in products:
            result += " and product = '" + _p + "'"
        result += "]"
        return result

    def get_latex_string(self):
        """Method to return the latex string for a reaction.

        Returns:
            :obj:`str`: The reaction string.

        """

        l_reactants = []
        for _r in self.reactants:
            l_reactants.append(self._create_latex_string(_r))

        l_products = []
        for _p in self.products:
            l_products.append(self._create_latex_string(_p))

        _s = r"$"
        _s += " + ".join(l_reactants)
        _s += " \\to "
        _s += " + ".join(l_products)
        _s += "$"
        return _s

    def get_data(self):
        """Method to return the data for a reaction.

        Returns:
            :obj:`dict`: A dictionary containing the rate data for the
            reaction.

        """
        return self.data

    def get_string(self):
        """Method to return the string for a reaction.

        Returns:
            :obj:`str`: The reaction string.

        """

        _s = " + ".join(self.reactants)
        _s += " -> "
        _s += " + ".join(self.products)
        return _s


class Xml(wb.Base):
    """A class for reading and plotting webnucleo xml files.

    Each instance corresponds to an xml file.  Methods extract
    data and plot data from the file.

    Args:
        ``file`` (:obj:`str`): The name of the xml file.

    """

    def __init__(self, file):
        parser = etree.XMLParser(remove_blank_text=True)
        self._xml = etree.parse(file, parser)
        self._xml.xinclude()
        self._root = self._xml.getroot()

    def _get_state_data(self, state_data, node):
        data = {}
        if node.xpath("@id"):
            data["state"] = (node.xpath("@id"))[0]
        else:
            data["state"] = ""
        if node.xpath("source"):
            data["source"] = (node.xpath("source"))[0].text
        else:
            data["source"] = ""
        data["mass excess"] = float((node.xpath("mass_excess"))[0].text)
        data["spin"] = float((node.xpath("spin"))[0].text)
        partf = node.xpath("partf_table/point")
        data["t9"] = np.zeros(len(partf))
        data["partf"] = np.zeros(len(partf))
        for i, elem in enumerate(partf):
            data["t9"][i] = float((elem.xpath("t9")[0].text).strip())
            data["partf"][i] = np.power(
                10.0, float((elem.xpath("log10_partf")[0].text).strip())
            ) * (2.0 * data["spin"] + 1.0)
        ind = data["t9"].argsort()
        data["t9"] = data["t9"][ind]
        data["partf"] = data["partf"][ind]

        state_data.update(data)

    def _get_nuclide_data_array(self, nuc_xpath):
        result = []

        nuclides = self._root.xpath("//nuclear_data/nuclide" + nuc_xpath)

        for nuc in nuclides:
            data = {}
            data["z"] = int((nuc.xpath("z"))[0].text)
            data["a"] = int((nuc.xpath("a"))[0].text)
            data["n"] = data["a"] - data["z"]
            if nuc.xpath("states"):
                for state in nuc.xpath("states/state"):
                    state_data = {}
                    state_data.update(data)
                    self._get_state_data(state_data, state)
                    result.append(state_data)
            else:
                self._get_state_data(data, nuc)
                result.append(data)

        return result

    def get_type(self):
        """Method to retrieve the root type of the webnucleo XML.

        Returns:
            :obj:`str`: One of `nuclear_data`, `reaction_data`,
            `nuclear_network`, `zone_data`, `libnucnet_input` indicating
            the root type of the XML.

        """

        return self._root.tag

    def get_nuclide_data(self, nuc_xpath=" "):
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
        for i, nuc in enumerate(nuclides):
            _s = self.create_nuclide_name(nuc["z"], nuc["a"], nuc["state"])
            result[_s] = nuclides[i]

        return result

    def get_network_limits(self, nuc_xpath=" "):
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

        n_d = self._get_nuclide_data_array(nuc_xpath)

        z_s = set()

        for _nnd in n_d:
            if _nnd["z"] not in z_s:
                z_s.add(_nnd["z"])

        z_t = []
        for z_z in z_s:
            z_t.append(z_z)

        z_t.sort()

        zlim = [[] for i in range(len(z_t))]

        for n_nd in n_d:
            loc = [j for j, zj in enumerate(z_t) if zj == n_nd["z"]]
            zlim[loc[0]].append(n_nd["n"])

        _z = np.zeros(len(zlim), dtype=np.int_)
        n_min = np.zeros(len(zlim), dtype=np.int_)
        n_max = np.zeros(len(zlim), dtype=np.int_)

        for i, z_zlim in enumerate(zlim):
            _z[i] = int(z_t[i])
            n_min[i] = int(min(z_zlim))
            n_max[i] = int(max(z_zlim))

        return {"z": _z, "n_min": n_min, "n_max": n_max}

    def _get_nuclide_data_for_zone(self, zone):
        result = {}

        species = zone.xpath("mass_fractions/nuclide")

        for s_sp in species:
            _z = int((s_sp.xpath("z"))[0].text)
            _a = int((s_sp.xpath("a"))[0].text)
            name_array = s_sp.xpath("@name")
            if len(name_array) == 0:
                name = self.create_nuclide_name(_z, _a, "")
            else:
                name = name_array[0]
            result[(name, _z, _a)] = float((s_sp.xpath("x"))[0].text)

        return result

    def _get_reaction_data_array(self, reac_xpath):
        result = []

        reactions = self._root.xpath("//reaction_data/reaction" + reac_xpath)

        for reaction_node in reactions:
            _r = Reaction()

            if reaction_node.xpath("source"):
                _r.source = reaction_node.xpath("source")[0].text

            reactants = reaction_node.xpath("reactant")

            for reactant in reactants:
                _r.reactants.append(reactant.text)
                if not _r.is_non_nuclide_reaction_element_string(
                    reactant.text
                ):
                    _r.nuclide_reactants.append(reactant.text)

            products = reaction_node.xpath("product")

            for product in products:
                _r.products.append(product.text)
                if not _r.is_non_nuclide_reaction_element_string(product.text):
                    _r.nuclide_products.append(product.text)

            _r.data = self._get_reaction_data(reaction_node)

            result.append(_r)

        return result

    def _get_non_smoker_data(self, non_smoker):
        result = {}
        result["type"] = non_smoker.tag

        def set_fit_data(node):
            fit_data = {}
            tags = [
                "Zt",
                "At",
                "Zf",
                "Af",
                "Q",
                "spint",
                "spinf",
                "TlowHf",
                "Tlowfit",
                "Thighfit",
                "acc",
                "a1",
                "a2",
                "a3",
                "a4",
                "a5",
                "a6",
                "a7",
                "a8",
            ]

            for tag in tags:
                datum = node.xpath(tag)
                if datum:
                    fit_data[tag] = float(datum[0].text)

            return fit_data

        fits = non_smoker.xpath("fit")
        result["fits"] = []

        if fits:
            for fit in fits:
                data = {}
                note = fit.xpath("@note")
                if note:
                    data["note"] = note[0]
                data = self._merge_dicts(data, set_fit_data(fit))
                result["fits"].append(data)

        else:
            result["fits"].append(set_fit_data(non_smoker))

        return result

    def _get_rate_table_data(self, rate_table):
        result = {}
        result["type"] = rate_table.tag
        table = rate_table.xpath("point")
        result["t9"] = np.zeros(len(table))
        result["rate"] = np.zeros(len(table))
        result["sef"] = np.zeros(len(table))
        for i, elem in enumerate(table):
            result["t9"][i] = float((elem.xpath("t9")[0].text).strip())
            result["rate"][i] = float((elem.xpath("rate")[0].text).strip())
            result["sef"][i] = float((elem.xpath("sef")[0].text).strip())

        ind = result["t9"].argsort()
        result["t9"] = result["t9"][ind]
        result["rate"] = result["rate"][ind]
        result["sef"] = result["sef"][ind]

        return result

    def _get_single_rate_data(self, single_rate):
        result = {}
        result["type"] = single_rate.tag
        result["rate"] = float(single_rate.text)

        return result

    def _get_user_rate_data(self, user_rate):
        result = {}
        result["type"] = user_rate.tag
        key = user_rate.xpath("@key")
        result["key"] = key[0]

        props = {}

        for prop in user_rate.xpath("properties/property"):
            name = prop.xpath("@name")
            tag1 = prop.xpath("@tag1")
            tag2 = prop.xpath("@tag2")

            key = name[0]
            if tag1:
                key = (name[0], tag1[0])
            if tag2:
                key += (tag2[0],)

            props[key] = prop.text

        result = self._merge_dicts(result, props)

        return result

    def _get_reaction_data(self, reaction_node):
        non_smoker = reaction_node.xpath("non_smoker_fit")
        if non_smoker:
            return self._get_non_smoker_data(non_smoker[0])

        rate_table = reaction_node.xpath("rate_table")
        if rate_table:
            return self._get_rate_table_data(rate_table[0])

        single_rate = reaction_node.xpath("single_rate")
        if single_rate:
            return self._get_single_rate_data(single_rate[0])

        user_rate = reaction_node.xpath("user_rate")
        if user_rate:
            return self._get_user_rate_data(user_rate[0])

        return None

    def get_reaction_data(self, reac_xpath=" "):
        """Method to retrieve reaction data from webnucleo XML.

        Args:
            ``reac_xpath`` (:obj:`str`, optional): XPath expression to select
            reactions.  Defaults to all reactions.

        Returns:
            :obj:`dict`: A dictionary of reaction data.  The data for each
            reaction are themselves contained in a :class:`Reaction`.

        """

        result = {}
        reactions = self._get_reaction_data_array(reac_xpath)
        for reaction in reactions:
            result[reaction.get_string()] = reaction

        return result

    def _get_zones(self, zone_xpath):
        return self._root.xpath("//zone_data/zone" + zone_xpath)

    def get_mass_fractions(self, species, zone_xpath=" "):
        """Method to retrieve mass fractions of nuclides in specified zones.

        Args:
            ``species`` (:obj:`list`): List of strings giving the species
            to retrieve.

            ``zone_xpath`` (:obj:`str`, optional): XPath expression to select
            zones.  Defaults to all zones.

        Returns:
            :obj:`dict`: A dictionary of :obj:`numpy.array` containing the
            mass fractions of the requested species in the zones as floats.

        """

        result = {}

        zones = self._get_zones(zone_xpath)

        for _sp in species:
            result[_sp] = np.zeros(len(zones))

        for i, zone in enumerate(zones):
            for _sp in species:
                data = zone.xpath(f'mass_fractions/nuclide[@name="{_sp}"]/x')
                if len(data) == 1:
                    result[_sp][i] = float(data[0].text)

        return result

    def get_properties(self, properties, zone_xpath=" "):
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

        for prop in properties:
            if isinstance(prop, str):
                properties_t[prop] = (prop,)
            else:
                properties_t[prop] = prop
                if len(properties_t[prop]) > 3:
                    print("\nToo many property names (at most 3)!\n")
                    return None

        my_dict = {}

        for prop in properties:
            my_dict[prop] = []

        zones = self._get_zones(zone_xpath)

        for zone in zones:
            for prop in properties:
                tup = properties_t[prop]

                path = "optional_properties/property"

                if len(tup) == 1:
                    path += f'[@name="{tup[0].strip()}"]'
                elif len(tup) == 2:
                    path += (
                        f'[@name="{tup[0].strip()}" and'
                        f' @tag1="{tup[1].strip()}"]'
                    )
                else:
                    path += (
                        f'[@name="{tup[0].strip()}" and'
                        f' @tag1="{tup[1].strip()}" and'
                        f' @tag2="{tup[2].strip()}"]'
                    )

                data = zone.xpath(path)

                if len(data) == 0:
                    print(
                        "Property", self._get_property_name(tup), "not found."
                    )
                    return None

                my_dict[prop].append(data[0].text)

        return my_dict

    def _get_all_zone_properties(self, zone):
        result = {}

        props = zone.xpath("optional_properties/property")

        for prop in props:
            p_name = ""
            name = prop.xpath("@name")
            tag1 = prop.xpath("@tag1")
            tag2 = prop.xpath("@tag2")
            if tag1:
                p_name = (name[0], tag1[0])
                if tag2:
                    p_name += (tag2[0],)
            else:
                p_name = name[0]
            result[p_name] = prop.text

        return result

    def get_all_properties_for_zone(self, zone_xpath):
        """Method to retrieve all properties in a zone in an xml file

        Args:
            ``zone_xpath`` (:obj:`str`): XPath expression to select
            zone.  Must evaluate to a single zone.

        Returns:
            :obj:`dict`: A dictionary containing all the properties in
            the zone as strings.

        """

        zones = self._get_zones(zone_xpath)

        if len(zones) != 1:
            print("Incorrect number of zones.")
            return None

        return self._get_all_zone_properties(zones[0])

    def get_properties_as_floats(self, properties, zone_xpath=" "):
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
            props[prop] = np.array(props[prop], np.float64)

        return props

    def get_all_abundances_in_zones(self, zone_xpath=" "):
        """Method to retrieve all abundances in zones.

        Args:
            ``zone_xpath`` (:obj:`str`, optional): XPath expression to select
            zones.  Defaults to all zones.

        Returns:
            :obj:`numpy.array`: A three-dimensional array in which the first
            index gives the zone, the second gives the atomic number,
            and the third gives the neutron number.  The array value
            is the abundance in the zone given by the first index of the
            species with atomic number and neutron number given by the second
            and third indices, respectively.  The abundance of the species is
            the sum of the abundances of all states of that species.

        """

        zones = self._get_zones(zone_xpath)

        lim = self.get_network_limits()
        z_max = np.max(lim["z"])
        n_max = np.max(lim["n_max"])

        result = np.zeros((len(zones), z_max + 1, n_max + 1))

        for i, zone in enumerate(zones):
            for key, value in self._get_nuclide_data_for_zone(zone).items():
                result[i, key[1], key[2] - key[1]] += value / key[2]

        return result

    def get_abundances_vs_nucleon_number(self, nucleon="a", zone_xpath=" "):
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

        if nucleon not in ("z", "n", "a"):
            print("nucleon must be 'z', 'n', or 'a'.")
            return None

        _y = self.get_all_abundances_in_zones(zone_xpath)

        if nucleon == "z":
            result = np.sum(_y, axis=2)
        elif nucleon == "n":
            result = np.sum(_y, axis=1)
        else:
            result = np.zeros((_y.shape[0], _y.shape[1] + _y.shape[2] + 2))
            for i in range(_y.shape[0]):
                for i_z in range(_y.shape[1]):
                    for i_n in range(_y.shape[2]):
                        result[i, i_z + i_n] += _y[i, i_z, i_n]

        return result

    def plot_property_vs_property(
        self,
        prop1,
        prop2,
        xfactor=1,
        yfactor=1,
        rcParams=None,
        plotParams=None,
        **kwargs,
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

        _x = result[prop1] / xfactor
        _y = result[prop2] / yfactor

        if plotParams:
            plt.plot(_x, _y, **plotParams)
        else:
            plt.plot(_x, _y)

        if "xlabel" not in kwargs:
            plt.xlabel(prop1)

        if "ylabel" not in kwargs:
            plt.ylabel(prop2)

        self.apply_class_methods(plt, kwargs)

        self.show_or_close(plt, kwargs)

    def plot_mass_fractions_vs_property(
        self,
        prop,
        species,
        xfactor=1,
        use_latex_names=False,
        rcParams=None,
        plotParams=None,
        **kwargs,
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
                    "Number of plotParam elements must equal number"
                    + " of species."
                )
                return

        plots = []

        _x = self.get_properties_as_floats([prop])[prop] / xfactor

        _y = self.get_mass_fractions(species)

        if use_latex_names:
            latex_names = self.get_latex_names(species)

        for i, s_sp in enumerate(species):
            if plotParams is None:
                _p = {}
            else:
                _p = plotParams[i]
            if "label" not in _p:
                if use_latex_names:
                    _p = self._merge_dicts(_p, {"label": latex_names[s_sp]})
                else:
                    _p = self._merge_dicts(_p, {"label": s_sp})
            plots.append(plt.plot(_x, _y[s_sp], **_p))

        if len(species) > 1 and "legend" not in kwargs:
            plt.legend()

        if "xlabel" not in kwargs:
            plt.xlabel(prop)

        if "ylabel" not in kwargs:
            if len(species) > 1:
                plt.ylabel("Mass Fraction")
            else:
                if use_latex_names:
                    _s = "$X(" + latex_names[species[0]][1:-1] + ")$"
                else:
                    _s = species[0]
                plt.ylabel(_s)

        self.apply_class_methods(plt, kwargs)

        self.show_or_close(plt, kwargs)

    def plot_abundances_vs_nucleon_number(
        self,
        nucleon="a",
        zone_xpath="[last()]",
        rcParams=None,
        plotParams=None,
        **kwargs,
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

        _y = self.get_abundances_vs_nucleon_number(nucleon, zone_xpath)

        if plotParams:
            if _y.shape[0] != len(plotParams):
                print(
                    "Number of plotParam elements must equal number of plots."
                )
                return

        for i in range(_y.shape[0]):
            if plotParams:
                plt.plot(_y[i, :], **plotParams[i])
            else:
                plt.plot(_y[i, :])

        if "xlabel" not in kwargs:
            plt.xlabel(nucleon)

        if "ylabel" not in kwargs:
            _s = "Y(" + nucleon + ")"
            plt.ylabel(_s)

        if "legend" not in kwargs:
            if plotParams:
                if "label" in plotParams[0]:
                    plt.legend()

        self.apply_class_methods(plt, kwargs)

        self.show_or_close(plt, kwargs)

    def get_chain_abundances(self, nucleon, zone_xpath="", vs_A=False):
        """Method to retrieve the abundances in a chain (fixed Z or N).

        Args:

            ``nucleon`` (:obj:`tuple`, optional): A tuple giving the nucleon.
            The first entry must be the nucleon type (must be 'z' or 'n') while
            the second entry must be the value.

            ``zone_xpath`` (:obj:`str`, optional): A string giving the XPath
            expression to select the zones. Defaults to all zones.

            ``vs_A`` (:obj:`bool`, optional): A boolean to select whether
            abscissa data should be mass number.

        Returns:
            A :obj:`tuple` containing an array of the nucleon values as the
            first element and a two-d :obj:`numpy.array` as the second element.
            The first index of the two-d array indicates the step and the
            second the abundance of the species with the corresponding nucleon
            number in the first element with the same index.

        """
        abunds = self.get_all_abundances_in_zones(zone_xpath=zone_xpath)

        assert nucleon[0] in ("z", "n"), "Invalid nucleon"

        if nucleon[0] == "z":
            _x = range(abunds.shape[2])
            _y = abunds[:, nucleon[1], :]
        else:
            _x = range(abunds.shape[1])
            _y = abunds[:, :, nucleon[1]]

        if vs_A:
            _x = [x_x + nucleon[1] for x_x in _x]

        return (_x, _y)

    def make_abundance_chain_movie(
        self,
        movie_name=None,
        nucleon=("z", 26),
        zone_xpath="",
        plot_vs_A=False,
        fps=15,
        title_func=None,
        rcParams=None,
        plotParams=None,
        extraFixedCurves=None,
        extraCurves=None,
        **kwargs,
    ):
        """Method to make of movie of abundances in a chain (fixed Z or N).

        Args:

            ``movie_name`` (:obj:`str`, optional): A string giving the name of
            resulting movie file.

            ``nucleon`` (:obj:`tuple`, optional): A tuple giving the nucleon.
            The first entry must be the nucleon type (must be 'z' or 'n') while
            the second entry must be the value.

            ``zone_xpath`` (:obj:`str`, optional): A string giving the XPath
            expression to select the zones. Defaults to all zones.

            ``plot_vs_A`` (:obj:`bool`, optional): A boolean to select whether
            abscissa should be mass number.

            ``fps`` (:obj:`float`, optional): A float giving the frames
            per second in the resulting movie.

            ``title_func`` (optional):
            A
            `function \
            <https://docs.python.org/3/library/stdtypes.html#functions>`_
            that applies the title to each frame of the movie.  The function
            must take a single argument, an :obj:`int` giving the index of the
            frame to which the title will be applied.  Other data can be bound
            to the function.  The function must return either a :obj:`str`
            giving the title or a two-element :obj:`tuple` in which the
            first element is a string giving the title and the second element
            is a :obj:`dict` with optional :obj:`matplotlib.pyplot.title`
            keyword arguments.  The default is a title giving the time in
            seconds, the temperature in billions of Kelvins, and the
            mass density in grams / cc.

            ``rcParams`` (:obj:`dict`, optional): A dictionary of
            :obj:`matplotlib.rcParams` to be applied to the movie.
            Defaults to the default rcParams.

            ``plotParams`` (:obj:`list`, optional): A list of
            dictionaries of valid :obj:`matplotlib.pyplot.plot` optional
            keyword arguments to be applied to the lines in the movie.

            ``extraFixedCurves`` (:obj:`list`, optional): A list of
            :obj:`tuple` objects giving fixed curves to appear on each
            frame of the animation.  The first element of the tuple is a
            :obj:`list` giving the abscissa values for the curve, the second
            element is the ordinate values for the curve, and the third
            element, if present, is a :obj:`dict` of
            :obj:`matplotlib.pyplot.plot` optional keyword arguments to be
            applied to the extra fixed curves in the movie.

            ``extraCurves`` (:obj:`list`, optional): A list of
            :obj:`tuple` objects giving curves to appear on each
            frame of the animation.  The first element of the tuple is a
            :obj:`list` giving the abscissa values for the curve, the second
            element is a two-d :obj:`numpy.array` giving the ordinate values
            for the curve corresponding to each timestep in the animation,
            and the third element, if present, is a :obj:`dict` of
            :obj:`matplotlib.pyplot.plot` optional keyword arguments to be
            applied to the extra fixed curves in the movie.


            ``**kwargs``:  Acceptable :obj:`matplotlib.pyplot` functions.
            Include directly, as a :obj:`dict`, or both.

        Returns:
            The animation.

        """
        fig = plt.figure()

        self.set_plot_params(mpl, rcParams)

        _x, _y = self.get_chain_abundances(
            nucleon, zone_xpath=zone_xpath, vs_A=plot_vs_A
        )
        props = self.get_properties_as_floats(
            ["time", "t9", "rho"], zone_xpath=zone_xpath
        )

        # Check the array length against the number of steps

        if extraCurves:
            for tup in extraCurves:
                if tup[1].shape[0] != _y.shape[0]:
                    print("Extra curve does not have the right length.")
                    return None

        def updatefig(i):
            fig.clear()

            if plotParams:
                plt.plot(_x, _y[i], **plotParams)
            else:
                plt.plot(_x, _y[i])

            if extraFixedCurves:
                for tup in extraFixedCurves:
                    if len(tup) == 2:
                        plt.plot(tup[0], tup[1])
                    else:
                        plt.plot(tup[0], tup[1], **tup[2])

            if extraCurves:
                for tup in extraCurves:
                    if len(tup) == 2:
                        plt.plot(tup[0], tup[1][i])
                    else:
                        plt.plot(tup[0], tup[1][i], **tup[2])

            if title_func:
                t_f = title_func(i)
                if t_f:
                    if isinstance(t_f, tuple):
                        plt.title(t_f[0], **t_f[1])
                    elif isinstance(t_f, str):
                        plt.title(t_f)
                    else:
                        print("Invalid return from title function.")
                        return
            else:
                if nucleon[0] == "z":
                    pre_str = f"Z = {nucleon[1]:d}, "
                else:
                    pre_str = f"N = {nucleon[1]:d}, "
                title_str = pre_str + self.make_time_t9_rho_title_str(props, i)
                plt.title(title_str)
            if "xlabel" not in kwargs:
                if not plot_vs_A:
                    if nucleon[0] == "z":
                        plt.xlabel("N")
                    else:
                        plt.xlabel("Z")
                else:
                    plt.xlabel("A")
            if "ylabel" not in kwargs:
                plt.ylabel("Abundance per nucleon")
            self.apply_class_methods(plt, kwargs)
            plt.draw()

        anim = animation.FuncAnimation(fig, updatefig, _y.shape[0])
        if movie_name:
            anim.save(movie_name, fps=fps)

        return anim

    def make_abundances_vs_nucleon_number_movie(
        self,
        movie_name="",
        nucleon="a",
        zone_xpath="",
        fps=15,
        title_func=None,
        rcParams=None,
        plotParams=None,
        extraFixedCurves=None,
        extraCurves=None,
        **kwargs,
    ):
        """Method to make of movie of abundances summed by nucleon number.

        Args:

            ``movie_name`` (:obj:`str`, optional): A string giving the name of
            resulting movie file.

            ``nucleon`` (:obj:`str`, optional): A string giving the nucleon
            (must be 'z', 'n', or 'a').  Defaults to 'a'.

            ``zone_xpath`` (:obj:`str`, optional): A string giving the XPath
            expression to select the zones. Defaults to all zones.

            ``fps`` (:obj:`float`, optional): A float giving the frames
            per second in the resulting movie file.

            ``title_func`` (optional):
            A
            `function \
            <https://docs.python.org/3/library/stdtypes.html#functions>`_
            that applies the title to each frame of the movie.  The function
            must take a single argument, an :obj:`int` giving the index of the
            frame to which the title will be applied.  Other data can be bound
            to the function.  The function must return either a :obj:`str`
            giving the title or a two-element :obj:`tuple` in which the
            first element is a string giving the title and the second element
            is a :obj:`dict` with optional :obj:`matplotlib.pyplot.title`
            keyword arguments.  The default is a title giving the time in
            seconds, the temperature in billions of Kelvins, and the
            mass density in grams / cc.

            ``rcParams`` (:obj:`dict`, optional): A dictionary of
            :obj:`matplotlib.rcParams` to be applied to the movie.
            Defaults to the default rcParams.

            ``plotParams`` (:obj:`list`, optional): A list of
            dictionaries of valid :obj:`matplotlib.pyplot.plot` optional
            keyword arguments to be applied to the lines in the movie.

            ``extraFixedCurves`` (:obj:`list`, optional): A list of
            :obj:`tuple` objects giving fixed curves to appear on each
            frame of the animation.  The first element of the tuple is a
            :obj:`list` giving the abscissa values for the curve, the second
            element is the ordinate values for the curve, and the third
            element, if present, is a :obj:`dict` of
            :obj:`matplotlib.pyplot.plot` optional keyword arguments to be
            applied to the extra fixed curves in the movie.

            ``extraCurves`` (:obj:`list`, optional): A list of
            :obj:`tuple` objects giving curves to appear on each
            frame of the animation.  The first element of the tuple is a
            :obj:`list` giving the abscissa values for the curve, the second
            element is a two-d :obj:`numpy.array` giving the ordinate values
            for the curve corresponding to each timestep in the animation,
            and the third element, if present, is a :obj:`dict` of
            :obj:`matplotlib.pyplot.plot` optional keyword arguments to be
            applied to the extra fixed curves in the movie.

            ``**kwargs``:  Acceptable :obj:`matplotlib.pyplot` functions.
            Include directly, as a :obj:`dict`, or both.

        Returns:
            The animation.

        """
        fig = plt.figure()

        self.set_plot_params(mpl, rcParams)

        abunds = self.get_abundances_vs_nucleon_number(
            nucleon=nucleon, zone_xpath=zone_xpath
        )
        props = self.get_properties_as_floats(
            ["time", "t9", "rho"], zone_xpath=zone_xpath
        )

        # Check the array length against the number of steps

        if extraCurves:
            for tup in extraCurves:
                if tup[1].shape[0] != abunds.shape[0]:
                    print("Extra curve does not have the right length.")
                    return None

        def updatefig(i):
            fig.clear()

            if plotParams:
                plt.plot(abunds[i, :], **plotParams)
            else:
                plt.plot(abunds[i, :])

            if extraFixedCurves:
                for tup in extraFixedCurves:
                    if len(tup) == 2:
                        plt.plot(tup[0], tup[1])
                    else:
                        plt.plot(tup[0], tup[1], **tup[2])

            if extraCurves:
                for tup in extraCurves:
                    if len(tup) == 2:
                        plt.plot(tup[0], tup[1][i])
                    else:
                        plt.plot(tup[0], tup[1][i], **tup[2])

            if title_func:
                t_f = title_func(i)
                if t_f:
                    if isinstance(t_f, tuple):
                        plt.title(t_f[0], **t_f[1])
                    elif isinstance(t_f, str):
                        plt.title(t_f)
                    else:
                        print("Invalid return from title function.")
                        return
            else:
                plt.title(self.make_time_t9_rho_title_str(props, i))
            if "xlabel" not in kwargs:
                plt.xlabel(nucleon)
            if "ylabel" not in kwargs:
                plt.ylabel("Y(" + nucleon + ")")
            self.apply_class_methods(plt, kwargs)
            plt.draw()

        anim = animation.FuncAnimation(fig, updatefig, abunds.shape[0])
        if movie_name:
            anim.save(movie_name, fps=fps)

        return anim

    def make_network_abundances_movie(
        self,
        movie_name="",
        zone_xpath="",
        fps=15,
        title_func=None,
        rcParams=None,
        imParams=None,
        show_limits=True,
        plotParams=None,
        **kwargs,
    ):
        """Method to make of movie of network abundances.

        Args:

            ``movie_name`` (:obj:`str`, optional): A string giving the name of
            resulting movie file.

            ``zone_xpath`` (:obj:`str`, optional): A string giving the XPath
            expression to select the zones. Defaults to all zones.

            ``fps`` (:obj:`float`, optional): A float giving the frames
            per second in the resulting movie file.

            ``title_func`` (optional):
            A
            `function \
            <https://docs.python.org/3/library/stdtypes.html#functions>`_
            that applies the title to each frame of the movie.  The function
            must take a single argument, an :obj:`int` giving the index of the
            frame to which the title will be applied.  Other data can be bound
            to the function.  The function must return either a :obj:`str`
            giving the title or a two-element :obj:`tuple` in which the
            first element is a string giving the title and the second element
            is a :obj:`dict` with optional :obj:`matplotlib.pyplot.title`
            keyword arguments.  The default is a title giving the time in
            seconds, the temperature in billions of Kelvins, and the
            mass density in grams / cc.

            ``rcParams`` (:obj:`dict`, optional): A dictionary of
            :obj:`matplotlib.rcParams` to be applied to the movie.
            Defaults to the default rcParams.

            ``imParams`` (:obj:`dict`, optional): A dictionary of
            :obj:`matplotlib.pyplot.imshow` options to be applied to the
            movie.  The default is equivalent to calling with
            imParams={'origin':'lower', 'cmap': cm.BuPu, 'norm': LogNorm(),
            'vmin': 1.e-10, 'vmax': 1}.  `cm` in this call is the
            :obj:`matplotlib.cm` namespace.  Any or all of these options
            can be overridden or others added by
            setting any of them in the input :obj:`dict`.

            ``plotParams`` (:obj:`list`, optional): A list of
            dictionaries of valid :obj:`matplotlib.pyplot.plot` optional
            keyword arguments to be applied to the network limits.
            Defaults are shown in the usage statement.

            ``**kwargs``:  Acceptable :obj:`matplotlib.pyplot` functions.
            Include directly, as a :obj:`dict`, or both.

        Returns:
            The animation.

        """

        if plotParams is None:
            plotParams = {"color": "black"}

        fig = plt.figure()

        self.set_plot_params(mpl, rcParams)

        abunds = self.get_all_abundances_in_zones(zone_xpath=zone_xpath)
        props = self.get_properties_as_floats(
            ["time", "t9", "rho"], zone_xpath=zone_xpath
        )
        lim = self.get_network_limits()

        _xr = [0, abunds.shape[2]]
        _yr = [0, abunds.shape[1]]
        if "xlim" in kwargs:
            _xr = [kwargs["xlim"][0], kwargs["xlim"][1]]
        if "ylim" in kwargs:
            _yr = [kwargs["ylim"][0], kwargs["ylim"][1]]

        if imParams is None:
            imParams = {}
        if "origin" not in imParams:
            imParams = self._merge_dicts({"origin": "lower"}, imParams)
        if "cmap" not in imParams:
            imParams = self._merge_dicts({"cmap": cm.BuPu}, imParams)
        if "norm" not in imParams:
            imParams = self._merge_dicts({"norm": LogNorm()}, imParams)
        if "vmin" not in imParams:
            imParams = self._merge_dicts({"vmin": 1.0e-10}, imParams)
        if "vmax" not in imParams:
            imParams = self._merge_dicts({"vmax": 1.0}, imParams)

        def updatefig(i):
            fig.clear()
            _z = abunds[i, _yr[0] : _yr[1], _xr[0] : _xr[1]]
            plt.imshow(_z, **imParams)
            if show_limits:
                if plotParams:
                    plt.plot(lim["n_min"], lim["z"], **plotParams)
                    plt.plot(lim["n_max"], lim["z"], **plotParams)
                else:
                    plt.plot(lim["n_min"], lim["z"])
                    plt.plot(lim["n_max"], lim["z"])
            if title_func:
                t_f = title_func(i)
                if isinstance(t_f, str):
                    plt.title(t_f)
                elif isinstance(t_f, tuple):
                    plt.title(t_f[0], t_f[1])
                else:
                    print("Invalid return from title function.")
                    return
            else:
                plt.title(self.make_time_t9_rho_title_str(props, i))
            if "xlabel" not in kwargs:
                plt.xlabel("N, Neutron Number")
            if "ylabel" not in kwargs:
                plt.ylabel("Z, Atomic Number")
            self.apply_class_methods(plt, kwargs)
            plt.draw()

        anim = animation.FuncAnimation(fig, updatefig, abunds.shape[0])
        if movie_name:
            anim.save(movie_name, fps=fps)

        return anim

    def get_zone_data(self, zone_xpath=""):
        """Method to retrieve zone data from webnucleo XML.

        Args:
            ``zone_xpath`` (:obj:`str`, optional): XPath expression to select
            zones.  Defaults to all zones.

        Returns:
            :obj:`dict`: A dictionary of zone data.  The data for each
            zone are themselves two :obj:`dict`, one containing properties
            and one containing mass fractions.

        """

        zones = self._get_zones(zone_xpath)

        result = {}

        for zone in zones:
            label = "0"
            label_1 = zone.xpath("@label1")
            if label_1:
                label = label_1[0]
            label_2 = zone.xpath("@label2")
            if label_2:
                label = (label, label_2[0])
            label_3 = zone.xpath("@label3")
            if label_3:
                label = (label[0], label[1], label_3[0])
            result[label] = {
                "properties": self._get_all_zone_properties(zone),
                "mass fractions": self._get_nuclide_data_for_zone(zone),
            }

        return result


class New_Xml(wb.Base):
    """A class for creating webnucleo xml files.

    Each instance corresponds to new xml.  Methods set
    the nuclide, reaction, or zone data or write the xml to a file.

    Args:
        ``xml_type`` (:obj:`str`, optional): The type of xml file to
        be created ("nuclear_data", "reaction_data", "nuclear_network",
        "zone_data", or "libnucnet_input").  Defaults to "nuclear_network".

    """

    def __init__(self, xml_type="nuclear_network"):
        if xml_type not in [
            "nuclear_data",
            "reaction_data",
            "nuclear_network",
            "zone_data",
            "libnucnet_input",
        ]:
            print("Invalid xml_type.")
        self._root = etree.Element(xml_type)
        self._xml = etree.ElementTree(self._root)
        if xml_type == "nuclear_network":
            etree.SubElement(self._root, "nuclear_data")
            etree.SubElement(self._root, "reaction_data")
        elif xml_type == "libnucnet_input":
            nuclear_network = etree.SubElement(self._root, "nuclear_network")
            etree.SubElement(nuclear_network, "nuclear_data")
            etree.SubElement(nuclear_network, "reaction_data")
            etree.SubElement(self._root, "zone_data")

    def _set_xml_data_for_nuclide(self, nuclide_element, nuclide):
        states = nuclide_element.xpath("states")

        if len(states) > 0:
            states_element = states[0]
        else:
            etree.SubElement(nuclide_element, "z").text = str(nuclide["z"])
            etree.SubElement(nuclide_element, "a").text = str(nuclide["a"])
            state_element = nuclide_element

        if nuclide["state"]:
            if len(states) == 0:
                states_element = etree.SubElement(nuclide_element, "states")
            state_element = etree.SubElement(states_element, "state")
            state_element.set("id", nuclide["state"])
            etree.SubElement(state_element, "source").text = str(
                nuclide["source"]
            )
        else:
            etree.SubElement(state_element, "source").text = str(
                nuclide["source"]
            )

        etree.SubElement(state_element, "mass_excess").text = str(
            nuclide["mass excess"]
        )
        etree.SubElement(state_element, "spin").text = str(nuclide["spin"])

        partf_element = etree.SubElement(state_element, "partf_table")

        p_t9 = nuclide["t9"]
        partf = nuclide["partf"]

        for i, my_t9 in enumerate(p_t9):
            point = etree.SubElement(partf_element, "point")
            etree.SubElement(point, "t9").text = str(my_t9)
            log10_partf = np.log10(partf[i] / (2.0 * nuclide["spin"] + 1))
            etree.SubElement(point, "log10_partf").text = str(log10_partf)

    def set_nuclide_data(self, nuclides):
        """Method to set the nuclide data.

        Args:

            ``nuclides`` (:obj:`dict`): A dictionary containing the nuclides
            to be created and their data.

        Returns:
            On successful return, the underlying xml has been created with
            the data in ``nuclides``.

        """

        nuclear_data = self._xml.xpath("//nuclear_data")

        if len(nuclear_data) == 0:
            print("Attempting to set non-existent nuclear_data.")
            return

        for nuc in nuclides:
            my_nuc = nuclides[nuc]
            my_xpath = self._xml.xpath(
                "//nuclear_data/nuclide[ z = "
                + str(my_nuc["z"])
                + " and a = "
                + str(my_nuc["a"])
                + "]"
            )
            if len(my_xpath) == 0:
                nuclear_data[0].append(
                    etree.Comment(
                        self.create_nuclide_name(my_nuc["z"], my_nuc["a"], "")
                    )
                )
                nuclide = etree.SubElement(nuclear_data[0], "nuclide")
            else:
                nuclide = my_xpath[0]
            self._set_xml_data_for_nuclide(nuclide, nuclides[nuc])

    def _set_xml_data_for_reaction(self, reaction_element, reaction):
        etree.SubElement(reaction_element, "source").text = str(
            reaction.source
        )

        for reactant in reaction.reactants:
            etree.SubElement(reaction_element, "reactant").text = str(reactant)

        for product in reaction.products:
            etree.SubElement(reaction_element, "product").text = str(product)

        if reaction.data["type"] == "single_rate":
            etree.SubElement(reaction_element, "single_rate").text = str(
                reaction.data["rate"]
            )
        elif reaction.data["type"] == "rate_table":
            rate_table_element = etree.SubElement(
                reaction_element, "rate_table"
            )
            my_t9 = reaction.data["t9"]
            my_rate = reaction.data["rate"]
            my_sef = reaction.data["sef"]
            for i, p_t9 in enumerate(my_t9):
                point = etree.SubElement(rate_table_element, "point")
                etree.SubElement(point, "t9").text = str(p_t9)
                etree.SubElement(point, "rate").text = str(my_rate[i])
                etree.SubElement(point, "sef").text = str(my_sef[i])
        elif reaction.data["type"] == "non_smoker_fit":
            nsf_element = etree.SubElement(reaction_element, "non_smoker_fit")
            for fit in reaction.data["fits"]:
                fit_element = etree.SubElement(nsf_element, "fit")
                for _d in fit:
                    if _d == "note":
                        fit_element.set("note", fit[_d])
                    else:
                        etree.SubElement(fit_element, _d).text = str(fit[_d])
        else:
            user_element = etree.SubElement(reaction_element, "user_rate")
            user_element.set("key", reaction.data["key"])
            properties = etree.SubElement(user_element, "properties")
            for _d in reaction.data:
                if _d not in ("type", "key"):
                    prop = etree.SubElement(properties, "property")
                    prop.text = str(reaction.data[_d])
                    if isinstance(_d, tuple):
                        prop.set("name", _d[0])
                        if len(_d) > 1:
                            prop.set("tag1", _d[1])
                            if len(_d) > 2:
                                prop.set("tag2", _d[2])
                        if len(_d) > 3:
                            print("Improper number of property tags.")
                            sys.exit()
                    else:
                        prop.set("name", _d)

    def set_reaction_data(self, reactions):
        """Method to set the reaction data.

        Args:

            ``reactions`` (:obj:`dict`): A dictionary containing the reactions
            to be set and their data.

        Returns:
            On successful return, the underlying xml has been created with
            the data in ``reactions``.

        """

        reaction_data = self._xml.xpath("//reaction_data")

        if len(reaction_data) == 0:
            print("Attempting to set non-existent reaction_data.")
            return

        for reaction in reactions:
            reaction_data[0].append(
                etree.Comment(reactions[reaction].get_string())
            )
            new_reaction = etree.SubElement(reaction_data[0], "reaction")
            self._set_xml_data_for_reaction(new_reaction, reactions[reaction])

    def _set_xml_data_for_zone(self, zone_element, zone):
        if len(zone["properties"]) > 0:
            props = etree.SubElement(zone_element, "optional_properties")
            for my_property in zone["properties"]:
                prop = etree.SubElement(props, "property")
                prop.text = str(zone["properties"][my_property])
                if isinstance(my_property, tuple):
                    prop.set("name", my_property[0])
                    if len(my_property) > 1:
                        prop.set("tag1", my_property[1])
                        if len(my_property) > 2:
                            prop.set("tag2", my_property[2])
                            if len(my_property) > 3:
                                print("Improper number of property tags.")
                                sys.exit()
                else:
                    prop.set("name", my_property)

        mass_fracs = etree.SubElement(zone_element, "mass_fractions")
        for nuc in zone["mass fractions"]:
            if zone["mass fractions"][nuc] != 0:
                nuclide = etree.SubElement(mass_fracs, "nuclide")
                nuclide.set("name", nuc[0])
                etree.SubElement(nuclide, "z").text = str(nuc[1])
                etree.SubElement(nuclide, "a").text = str(nuc[2])
                etree.SubElement(nuclide, "x").text = str(
                    zone["mass fractions"][nuc]
                )

    def set_zone_data(self, zones):
        """Method to set the zone data.

        Args:

            ``zones`` (:obj:`dict`): A dictionary containing the zones
            to be set and their data.

        Returns:
            On successful return, the underlying xml has been created with
            the data in ``reactions``.

        """

        zone_data = self._xml.xpath("//zone_data")

        if len(zone_data) == 0:
            print("Attempting to set non-existent zone_data.")
            return

        for zone in zones:
            new_zone = etree.SubElement(zone_data[0], "zone")
            if isinstance(zone, tuple):
                for i, zone_label in enumerate(zone):
                    label_str = "label" + str(i + 1)
                    new_zone.set(label_str, zone_label)
            else:
                new_zone.set("label1", zone)
            self._set_xml_data_for_zone(new_zone, zones[zone])

    def write(self, file, pretty_print=True):
        """Method to write the xml to a file.

        Args:

            ``file`` (:obj:`str`): A string giving the name of output
            xml file.

           ``pretty_print`` (:obj:`bool`, optional): If set to True,
           routine outputs the xml in nice indented format.

        Returns:
            On successful return, the underlying xml has been written
            to ``file``.

        """

        self._xml.write(file, pretty_print=pretty_print)
