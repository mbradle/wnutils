import wnutils.base as wb
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.colors import LogNorm
import matplotlib.animation as animation
import numpy as np
from lxml import etree
from scipy.interpolate import interp1d


class Reaction(wb.Base):
    """A class for storing and retrieving data about reactions.

       """

    def __init__(self):
        self.reactants = []
        self.products = []
        self.source = ""
        self.data = {}

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

        properties = user_rate.xpath("properties/property")

        props = {}

        for property in properties:
            name = property.xpath("@name")
            tag1 = property.xpath("@tag1")
            tag2 = property.xpath("@tag2")

            key = name[0]
            if tag1:
                key = (name[0], tag1[0])
            if tag2:
                key += (tag2[0],)

            props[key] = property.text

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

    def _set_data(self, reaction_node):
        self.source = reaction_node.xpath("source")[0].text

        reactants = reaction_node.xpath("reactant")
        for reactant in reactants:
            self.reactants.append(reactant.text)

        products = reaction_node.xpath("product")
        for product in products:
            self.products.append(product.text)

        self.data = self._get_reaction_data(reaction_node)

    def _compute_rate_table_rate(self, t9):
        t = self.data["t9"]
        lr = np.log10(self.data["rate"])
        sef = self.data["sef"]

        if len(t) <= 2:
            f1 = interp1d(t, lr, kind="linear")
            f2 = interp1d(t, sef, kind="linear")
            return np.power(10.0, f1(t9)) * f2(t9)
        else:
            f1 = interp1d(t, lr, kind="cubic")
            f2 = interp1d(t, sef, kind="cubic")
            return np.power(10.0, f1(t9)) * f2(t9)

    def _compute_non_smoker_fit_rate_for_fit(self, fit, t9):
        def non_smoker_function(fit, t9):
            x = (
                fit["a1"]
                + fit["a2"] / t9
                + fit["a3"] / np.power(t9, 1.0 / 3.0)
                + fit["a4"] * np.power(t9, 1.0 / 3.0)
                + fit["a5"] * t9
                + fit["a6"] * np.power(t9, 5.0 / 3.0)
                + fit["a7"] * np.log(t9)
            )
            return np.exp(x)

        if t9 < fit["Tlowfit"]:
            return non_smoker_function(fit, fit["Tlowfit"])
        elif t9 > fit["Thighfit"]:
            return non_smoker_function(fit, fit["Thighfit"])
        else:
            return non_smoker_function(fit, t9)

    def _compute_non_smoker_fit_rate(self, t9):
        fits = self.data["fits"]
        if len(fits) != 0:
            result = 0.0
            for fit in fits:
                result += self._compute_non_smoker_fit_rate_for_fit(fit, t9)
            return result
        else:
            return self._compute_non_smoker_fit_rate_for_fit(self.data, t9)

    def compute_rate(self, t9, user_funcs=" "):
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
        elif self.data["type"] == "rate_table":
            return self._compute_rate_table_rate(t9)
        elif self.data["type"] == "non_smoker_fit":
            return self._compute_non_smoker_fit_rate(t9)
        elif self.data["type"] == "user_rate":
            if self.data["key"] not in user_funcs:
                print("Function not defined for key " + self.data["key"])
                return None
            return user_funcs[self.data["key"]](self, t9)
        else:
            print("No such reaction type")
            return None

    def get_reactants(self):
        """Method to return the reactants for a reaction.

        Returns:
            :obj:`list`: A list of :obj:`str` giving the reactants.

        """
        return self.reactants

    def get_products(self):
        """Method to return the products for a reaction.

        Returns:
            :obj:`list`: A list of :obj:`str` giving the products.

        """
        return self.products

    def get_source(self):
        """Method to return the data source for a reaction.

        Returns:
            :obj:`str`: The source.

        """
        return self.source

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

        s = " + ".join(self.reactants)
        s += " -> "
        s += " + ".join(self.products)
        return s

    def get_latex_string(self):
        """Method to return the latex string for a reaction.

        Returns:
            :obj:`str`: The reaction string.

        """

        l_reactants = []
        for r in self.reactants:
            l_reactants.append(self._create_latex_string(r))

        l_products = []
        for p in self.products:
            l_products.append(self._create_latex_string(p))

        s = r"$"
        s += " + ".join(l_reactants)
        s += " \\to "
        s += " + ".join(l_products)
        s += "$"
        return s


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

        nuclides = self._root.xpath("//nuclear_data/nuclide" + nuc_xpath)

        for nuc in nuclides:
            data = {}
            data["z"] = int((nuc.xpath("z"))[0].text)
            data["a"] = int((nuc.xpath("a"))[0].text)
            data["n"] = data["a"] - data["z"]
            data["source"] = (nuc.xpath("source"))[0].text
            data["spin"] = float((nuc.xpath("spin"))[0].text)
            if nuc.xpath("state"):
                data["state"] = (nuc.xpath("state"))[0].text
            else:
                data["state"] = ""
            data["mass excess"] = float((nuc.xpath("mass_excess"))[0].text)
            partf = nuc.xpath("partf_table/point")
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
            result.append(data)

        return result

    def _get_max_nucleon_numbers(self):
        nd = self._get_nuclide_data_array("")

        z = np.zeros(len(nd), dtype=np.int_)
        n = np.zeros(len(nd), dtype=np.int_)
        a = np.zeros(len(nd), dtype=np.int_)

        for i in range(len(nd)):
            z[i] = nd[i]["z"]
            n[i] = nd[i]["n"]
            a[i] = nd[i]["a"]

        return {"z": np.amax(z), "n": np.amax(n), "a": np.amax(a)}

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
        for i in range(len(nuclides)):
            s = self.create_nuclide_name(
                nuclides[i]["z"], nuclides[i]["a"], nuclides[i]["state"]
            )
            result[s] = nuclides[i]

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

        nd = self._get_nuclide_data_array(nuc_xpath)

        zs = set()

        for i in range(len(nd)):
            if nd[i]["z"] not in zs:
                zs.add(nd[i]["z"])

        zt = []
        for zz in zs:
            zt.append(zz)

        zt.sort()

        zlim = [[] for i in range(len(zt))]

        for i in range(len(nd)):
            loc = [j for j, zj in enumerate(zt) if zj == nd[i]["z"]]
            zlim[loc[0]].append(nd[i]["n"])

        z = np.zeros(len(zlim), dtype=np.int_)
        n_min = np.zeros(len(zlim), dtype=np.int_)
        n_max = np.zeros(len(zlim), dtype=np.int_)

        for i in range(len(zlim)):
            z[i] = int(zt[i])
            n_min[i] = int(min(zlim[i]))
            n_max[i] = int(max(zlim[i]))

        return {"z": z, "n_min": n_min, "n_max": n_max}

    def _get_nuclide_data_for_zone(self, zone):
        result = {}

        species = zone.xpath("mass_fractions/nuclide")

        for sp in species:
            data = {}
            data["z"] = int((sp.xpath("z"))[0].text)
            data["a"] = int((sp.xpath("a"))[0].text)
            data["n"] = data["a"] - data["z"]
            data["x"] = float((sp.xpath("x"))[0].text)
            result[sp.xpath("@name")[0]] = data

        return result

    def _get_reaction_data_array(self, reac_xpath):
        result = []

        reactions = self._root.xpath("//reaction_data/reaction" + reac_xpath)

        for reaction in reactions:
            r = Reaction()
            r._set_data(reaction)

            result.append(r)

        return result

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

        for sp in species:
            result[sp] = np.zeros(len(zones))

        for i in range(len(zones)):
            for sp in species:
                data = zones[i].xpath(
                    'mass_fractions/nuclide[@name="%s"]/x' % sp
                )
                if len(data) == 1:
                    result[sp][i] = float(data[0].text)

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

        zones = self._get_zones(zone_xpath)

        for zone in zones:

            for property in properties:

                tup = properties_t[property]

                path = "optional_properties/property"

                if len(tup) == 1:
                    path += '[@name="%s"]' % tup[0].strip()
                elif len(tup) == 2:
                    path += '[@name="%s" and @tag1="%s"]' % (
                        tup[0].strip(),
                        tup[1].strip(),
                    )
                else:
                    path += '[@name="%s" and @tag1="%s" and @tag2="%s"]' % (
                        tup[0].strip(),
                        tup[1].strip(),
                        tup[2].strip(),
                    )

                data = zone.xpath(path)

                if len(data) == 0:
                    print(
                        "Property", self._get_property_name(tup), "not found."
                    )
                    return

                dict[property].append(data[0].text)

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
            print("Incorrect number of zones.")
            return

        props = zones[0].xpath("optional_properties/property")

        for property in props:
            p_name = ""
            name = property.xpath("@name")
            tag1 = property.xpath("@tag1")
            tag2 = property.xpath("@tag2")
            if tag1:
                p_name = (name[0], tag1[0])
                if tag2:
                    p_name += (tag2[0],)
            else:
                p_name = name[0]
            result[p_name] = property.text

        return result

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
            props[prop] = np.array(props[prop], np.float_)

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

        m = self._get_max_nucleon_numbers()

        result = np.zeros((len(zones), m["z"] + 1, m["n"] + 1))

        for i in range(len(zones)):
            sp = self._get_nuclide_data_for_zone(zones[i])

            for s in sp:
                result[i, sp[s]["z"], sp[s]["n"]] += sp[s]["x"] / sp[s]["a"]

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

        if nucleon != "z" and nucleon != "n" and nucleon != "a":
            print("nucleon must be 'z', 'n', or 'a'.")
            return

        zones = self._get_zones(zone_xpath)

        m = self._get_max_nucleon_numbers()

        result = np.zeros((len(zones), m[nucleon] + 1))

        for i in range(len(zones)):
            sp = self._get_nuclide_data_for_zone(zones[i])

            for s in sp:
                result[i, sp[s][nucleon]] += sp[s]["x"] / sp[s]["a"]

        return result

    def plot_property_vs_property(
        self,
        prop1,
        prop2,
        xfactor=1,
        yfactor=1,
        rcParams=None,
        plotParams=None,
        **kwargs
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

        x = result[prop1] / xfactor
        y = result[prop2] / yfactor

        if plotParams:
            plt.plot(x, y, **plotParams)
        else:
            plt.plot(x, y)

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
        **kwargs
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

        x = self.get_properties_as_floats([prop])[prop] / xfactor

        y = self.get_mass_fractions(species)

        if use_latex_names:
            latex_names = self.get_latex_names(species)

        for i, sp in enumerate(species):
            if plotParams is None:
                p = {}
            else:
                p = plotParams[i]
            if "label" not in p:
                if use_latex_names:
                    p = self._merge_dicts(p, {"label": latex_names[sp]})
                else:
                    p = self._merge_dicts(p, {"label": sp})
            plots.append(plt.plot(x, y[sp], **p))

        if len(species) > 1 and "legend" not in kwargs:
            plt.legend()

        if "xlabel" not in kwargs:
            plt.xlabel(prop)

        if "ylabel" not in kwargs:
            if len(species) > 1:
                plt.ylabel("Mass Fraction")
            else:
                if use_latex_names:
                    s = "$X(" + latex_names[species[0]][1:-1] + ")$"
                else:
                    s = species[0]
                plt.ylabel(s)

        self.apply_class_methods(plt, kwargs)

        self.show_or_close(plt, kwargs)

    def plot_abundances_vs_nucleon_number(
        self,
        nucleon="a",
        zone_xpath="[last()]",
        rcParams=None,
        plotParams=None,
        **kwargs
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

        y = self.get_abundances_vs_nucleon_number(nucleon, zone_xpath)

        if plotParams:
            if y.shape[0] != len(plotParams):
                print(
                    "Number of plotParam elements must equal number of plots."
                )
                return

        for i in range(y.shape[0]):
            if plotParams:
                plt.plot(y[i, :], **plotParams[i])
            else:
                plt.plot(y[i, :])

        if "xlabel" not in kwargs:
            plt.xlabel(nucleon)

        if "ylabel" not in kwargs:
            s = "Y(" + nucleon + ")"
            plt.ylabel(s)

        if "legend" not in kwargs:
            if plotParams:
                if "label" in plotParams[0]:
                    plt.legend()

        self.apply_class_methods(plt, kwargs)

        self.show_or_close(plt, kwargs)

    def make_abundances_vs_nucleon_number_movie(
        self,
        movie_name,
        nucleon="a",
        zone_xpath=" ",
        fps=15,
        title_func=None,
        rcParams=None,
        plotParams=None,
        **kwargs
    ):
        """Method to make of movie of abundances summed by nucleon number.

        Args:

            ``movie_name`` (:obj:`str`): A string giving the name of the
            movie to be made.

            ``nucleon`` (:obj:`str`, optional): A string giving the nucleon
            (must be 'z', 'n', or 'a').  Defaults to 'a'.

            ``zone_xpath`` (:obj:`str`, optional): A string giving the XPath
            expression to select the zones. Defaults to all zones.

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

            ``**kwargs``:  Acceptable :obj:`matplotlib.pyplot` functions.
            Include directly, as a :obj:`dict`, or both.

        Returns:
            A matplotlib plot.

        """
        fig = plt.figure()

        self.set_plot_params(mpl, rcParams)

        abunds = self.get_abundances_vs_nucleon_number(
            nucleon=nucleon, zone_xpath=zone_xpath
        )
        props = self.get_properties_as_floats(
            ["time", "t9", "rho"], zone_xpath=zone_xpath
        )

        def updatefig(i):
            fig.clear()
            if plotParams:
                plt.plot(abunds[i, :], **plotParams)
            else:
                plt.plot(abunds[i, :])
            if title_func:
                tf = title_func(i)
                if tf:
                    if type(tf) is tuple:
                        plt.title(tf[0], **tf[1])
                    elif type(tf) is str:
                        plt.title(tf)
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
        anim.save(movie_name, fps=fps)

    def make_network_abundances_movie(
        self,
        movie_name,
        zone_xpath=" ",
        fps=15,
        title_func=None,
        rcParams=None,
        imParams={},
        show_limits=True,
        plotParams={"color": "black"},
        **kwargs
    ):
        """Method to make of movie of network abundances.

        Args:

            ``movie_name`` (:obj:`str`): A string giving the name of the
            movie to be made.

            ``zone_xpath`` (:obj:`str`, optional): A string giving the XPath
            expression to select the zones. Defaults to all zones.

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
            A matplotlib plot.

        """

        fig = plt.figure()

        self.set_plot_params(mpl, rcParams)

        abunds = self.get_all_abundances_in_zones(zone_xpath=zone_xpath)
        props = self.get_properties_as_floats(
            ["time", "t9", "rho"], zone_xpath=zone_xpath
        )
        lim = self.get_network_limits()

        xr = [0, abunds.shape[2]]
        yr = [0, abunds.shape[1]]
        if "xlim" in kwargs:
            xr = [kwargs["xlim"][0], kwargs["xlim"][1]]
        if "ylim" in kwargs:
            yr = [kwargs["ylim"][0], kwargs["ylim"][1]]

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
            z = abunds[i, yr[0]: yr[1], xr[0]: xr[1]]
            plt.imshow(z, **imParams)
            if show_limits:
                if plotParams:
                    plt.plot(lim["n_min"], lim["z"], **plotParams)
                    plt.plot(lim["n_max"], lim["z"], **plotParams)
                else:
                    plt.plot(lim["n_min"], lim["z"])
                    plt.plot(lim["n_max"], lim["z"])
            if title_func:
                tf = title_func(i)
                if type(tf) is str:
                    plt.title(tf)
                elif type(tf) is tuple:
                    plt.title(tf[0], tf[1])
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
        anim.save(movie_name, fps=fps)
