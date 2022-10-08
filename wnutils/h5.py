import wnutils.base as wnb
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as animation
import warnings

with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=FutureWarning)
    import h5py


class H5(wnb.Base):
    """A class for reading and plotting webnucleo HDF5 files.

    Each instance corresponds to an hdf5 file.  Methods extract
    data and plot data from the file.

    Args:
        ``file`` (:obj:`str`): The name of the hdf5 file.

    """

    def __init__(self, file):
        self._h5file = h5py.File(file, "r")

    def _get_group_zone_property_hash(self, group, zone_index):

        properties = self._h5file["/" + group + "/Zone Properties/" + str(zone_index)]

        result = {}

        for property in properties:
            p0 = property[0].decode("ascii")
            p1 = property[1].decode("ascii")
            p2 = property[2].decode("ascii")
            name = ""
            if p1 == "0" and p2 == "0":
                name = p0
            elif p1 != "0" and p2 == "0":
                name = (p0, p1)
            else:
                name = (p0, p1, p2)
            result[name] = property[3].decode("ascii")

        return result

    def get_zone_labels_for_group(self, group):
        """Method to return zone labels for a group in a webnucleo hdf5 file.

        Args:
            ``group`` (:obj:`str`): The name of the group.

        Returns:
            :obj:`list`: A list of :obj:`tuple` giving the labels for the
            zones in a group.

        """

        zone_labels = self._h5file["/" + group + "/Zone Labels"]

        result = []

        for i in range(len(zone_labels)):
            result.append(
                (
                    zone_labels[i][0].decode("ascii"),
                    zone_labels[i][1].decode("ascii"),
                    zone_labels[i][2].decode("ascii"),
                )
            )

        return result

    def _get_group_zone_labels_hash(self, group):

        zone_labels_array = self.get_zone_labels_for_group(group)

        result = {}

        for i in range(len(zone_labels_array)):
            result[zone_labels_array[i]] = i

        return result

    def get_iterable_groups(self):
        """Method to return the non-nuclide data groups in an hdf5 file.

        Returns:
            :obj:`list`: A list of strings giving the names of the groups.

        """

        result = []

        for group_name in self._h5file:
            if group_name != "Nuclide Data":
                result.append(group_name)

        return result

    def _get_nuclide_data_array(self):

        result = []

        nuclide_data = self._h5file["/Nuclide Data"]

        for i in range(len(nuclide_data)):
            data = {}
            data["name"] = nuclide_data[i][0].decode("ascii")
            data["z"] = nuclide_data[i][2]
            data["a"] = nuclide_data[i][3]
            data["n"] = data["a"] - data["z"]
            data["source"] = nuclide_data[i][4].decode("ascii")
            data["state"] = nuclide_data[i][5].decode("ascii")
            data["mass excess"] = nuclide_data[i][6]
            data["spin"] = nuclide_data[i][7]
            result.append(data)

        return result

    def get_nuclide_data(self):
        """Method to return nuclide data from an hdf5 file.

        Returns:

            :obj:`dict`: A dictionary of the nuclide data.  Each
            entry is itself a dictionary containing the nuclide's index,
            name, z, a, source (data source), state, spin, and mass excess.

        """

        nuclide_data = self._get_nuclide_data_array()

        result = {}

        for i in range(len(nuclide_data)):
            data = {}
            data["index"] = i
            data["z"] = nuclide_data[i]["z"]
            data["a"] = nuclide_data[i]["a"]
            data["n"] = nuclide_data[i]["n"]
            data["source"] = nuclide_data[i]["source"]
            data["state"] = nuclide_data[i]["state"]
            data["mass excess"] = nuclide_data[i]["mass excess"]
            data["spin"] = nuclide_data[i]["spin"]
            result[nuclide_data[i]["name"]] = data

        return result

    def get_group_mass_fractions(self, group):
        """Method to return mass fractions from a group in an hdf5 file.

        Args:
            ``group`` (:obj:`str`): The name of the group.

        Returns:
            A 2d hdf5
            `dataset <https://docs.h5py.org/en/stable/high/dataset.html>`_.
            The first index indicates the zone and the second the species.

        """

        return self._h5file["/" + group + "/Mass Fractions"]

    def get_zone_mass_fractions_in_groups(self, zone, species):
        """Method to return zone mass fractions in all groups.

        Args:

            ``zone`` (:obj:`tuple`): A three element tuple giving the three
            labels for the zone.

            ``species`` (:obj:`list`): A list of strings giving the species
            whose mass fractions are to be retrieved.

        Returns:
            :obj:`dict`: A dictionary of :obj:`numpy.array` giving the
            mass fractions in the groups.

        """

        nuclide_hash = self.get_nuclide_data()

        result = {}

        for sp in species:
            result[sp] = np.array([])

        for group_name in self.get_iterable_groups():
            zone_index = self._get_group_zone_labels_hash(group_name)
            x = self.get_group_mass_fractions(group_name)
            for sp in species:
                result[sp] = np.append(
                    result[sp], x[zone_index[zone], nuclide_hash[sp]["index"]]
                )

        return result

    def get_group_zone_properties(self, group, zone):
        """Method to return all properties in a zone in a group.

        Args:

            ``group`` (:obj:`str`): A string giving the group name.

            ``zone`` (:obj:`tuple`): A three element tuple giving the three
            labels for the zone.

        Returns:
            :obj:`dict`: A dictionary of strings giving all the properties
            in the zone in the group.

        """

        zone_index = self._get_group_zone_labels_hash(group)[zone]
        return self._get_group_zone_property_hash(group, zone_index)

    def get_zone_properties_in_groups(self, zone, properties):
        """Method to return zone properties in all groups.

        Args:

            ``zone`` (:obj:`tuple`): A three element tuple giving the three
            labels for the zone.

            ``properties`` (:obj:`list`): A list of strings or tuples
            of up to three strings giving the properties to be retrieved.

        Returns:
            :obj:`dict`: A dictionary of :obj:`list` giving the properties
            in the groups as strings.

        """

        result = {}

        for property in properties:
            result[property] = []

        for group_name in self.get_iterable_groups():
            zone_index = self._get_group_zone_labels_hash(group_name)[zone]
            p = self._get_group_zone_property_hash(group_name, zone_index)
            for property in properties:
                result[property].append(p[property])

        return result

    def get_zone_properties_in_groups_as_floats(self, zone, properties):
        """Method to return zone properties in all groups as floats.

        Args:

            ``zone`` (:obj:`tuple`): A three element tuple giving the three
            labels for the zone.

            ``properties`` (:obj:`list`): A list of strings or tuples
            of up to three strings giving the properties to be retrieved.

        Returns:
            :obj:`dict`: A dictionary of :obj:`numpy.array` giving the
            properties in the groups as floats.

        """

        result = {}

        props = self.get_zone_properties_in_groups(zone, properties)

        for prop in props:
            result[prop] = np.array(props[prop], np.float_)

        return result

    def get_group_properties_in_zones(self, group, properties):
        """Method to return properties in all zones for a group.

        Args:

            ``group`` (:obj:`str`): A string giving the group name.

            ``properties`` (:obj:`list`): A list of strings or tuples
            of up to three strings giving the properties to be retrieved.

        Returns:
            :obj:`dict`: A dictionary of :obj:`list` giving the
            properties in the zones as strings.

        """

        result = {}

        for property in properties:
            result[property] = []

        zone_labels_hash = self._get_group_zone_labels_hash(group)

        for zone_labels in self.get_zone_labels_for_group(group):
            p = self._get_group_zone_property_hash(
                group,
                zone_labels_hash[(zone_labels[0], zone_labels[1], zone_labels[2])],
            )
            for property in properties:
                result[property].append(p[property])

        return result

    def get_group_properties_in_zones_as_floats(self, group, properties):
        """Method to return properties in all zones for a group as floats.

        Args:

            ``group`` (:obj:`str`): A string giving the group name.

            ``properties`` (:obj:`list`): A list of strings or tuples
            of up to three strings giving the properties to be retrieved.

        Returns:
            :obj:`dict`: A dictionary of :obj:`numpy.array` giving the
            properties in the zones as floats.

        """

        result = {}

        props = self.get_group_properties_in_zones(group, properties)

        for prop in props:
            result[prop] = np.array(props[prop], np.float_)

        return result

    def plot_zone_property_vs_property(
        self,
        zone,
        prop1,
        prop2,
        xfactor=1,
        yfactor=1,
        rcParams=None,
        plotParams=None,
        **kwargs
    ):
        """Method to plot a property vs. a property in a zone.

        Args:

            ``zone`` (:obj:`tuple`): A three element tuple giving the zone
            labels.

            ``prop1`` (:obj:`str` or :obj:`tuple`): A string or tuple
            of up to three strings giving the property (which will
            be the abscissa of the plot).

            ``prop2`` (:obj:`str` or :obj:`tuple`): A string or tuple
            of up to three strings giving the property (which will
            be the ordinate of the plot).

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

        result = self.get_zone_properties_in_groups_as_floats(zone, [prop1, prop2])

        x = result[prop1] / xfactor
        y = result[prop2] / yfactor

        if plotParams:
            plt.plot(x, y, **plotParams)
        else:
            plt.plot(x, y)

        self.apply_class_methods(plt, kwargs)

        self.show_or_close(plt, kwargs)

    def plot_group_mass_fractions(
        self,
        group,
        species,
        use_latex_names=False,
        rcParams=None,
        plotParams=None,
        **kwargs
    ):
        """Method to plot group mass fractions vs. zone.

        Args:

            ``group`` (:obj:`str`): A string giving the group.

            ``species`` (:obj:`list`): A list of strings giving the species to
            plot.

            ``use_latex_names`` (:obj:`bool`, optional): If set to True,
            species names converted to latex format.

            ``rcParams``` (:obj:`dict`, optional): A dictionary of
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
                print("Number of plotParam elements must equal" + " number of species.")
                return

        plots = []

        m = self.get_group_mass_fractions(group)

        nuclide_data = self.get_nuclide_data()

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
            plots.append(plt.plot(m[:, nuclide_data[sp]["index"]], **p))

        if len(species) != 1:
            plt.legend()

        if "ylabel" not in kwargs:
            if len(species) != 1:
                plt.ylabel("Mass Fraction")
            else:
                if use_latex_names:
                    plt.ylabel("X(" + latex_names[species[0]] + ")")
                else:
                    plt.ylabel("X(" + species[0] + ")")

        self.apply_class_methods(plt, kwargs)

        self.show_or_close(plt, kwargs)

    def plot_group_property_in_zones(
        self, group, property, rcParams=None, plotParams=None, **kwargs
    ):
        """Method to plot a group property vs. zone.

        Args:

            ``group`` (:obj:`str`): A string giving the group.

            ``property`` (:obj:`str` or :obj:`tuple`): A string or tuple
            of up to three strings giving the group.

            ``rcParams``` (:obj:`dict`, optional): A dictionary of
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

        prop = self.get_group_properties_in_zones_as_floats(group, [property])

        if plotParams:
            plt.plot(prop[property], **plotParams)
        else:
            plt.plot(prop[property])

        if "ylabel" not in kwargs:
            plt.ylabel(property)

        self.apply_class_methods(plt, kwargs)

        self.show_or_close(plt, kwargs)

    def plot_group_mass_fractions_vs_property(
        self,
        group,
        prop,
        species,
        xfactor=1,
        use_latex_names=False,
        rcParams=None,
        plotParams=None,
        **kwargs
    ):
        """Method to plot group mass fractions vs. zone property.

        Args:

            ``group`` (:obj:`str`): A string giving the group.

            ``prop`` (:obj:`str` or :obj:`tuple`): A string or tuple of
            up to three strings giving the property (which will
            serve as the plot abscissa).

            ``species`` (:obj:`list`): A list of strings giving the species
            to plot.

            ``xfactor`` (:obj:`float`, optional): A float giving the scaling
            for the abscissa values.  Defaults to 1.

            ``use_latex_names`` (:obj:`bool`, optional): If set to True,
            species names converted to latex format.

            ``rcParams``` (:obj:`dict`, optional): A dictionary of
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
                print("Number of plotParam elements must equal" + " number of species.")
                return

        plots = []

        x = self.get_group_properties_in_zones_as_floats(group, [prop])[prop]
        m = self.get_group_mass_fractions(group)

        nuclide_data = self.get_nuclide_data()

        if use_latex_names:
            latex_names = self.get_latex_names(species)

        for i, sp in enumerate(species):
            y = m[:, nuclide_data[sp]["index"]]
            if plotParams is None:
                p = {}
            else:
                p = plotParams[i]
            if "label" not in p:
                if use_latex_names:
                    p = self._merge_dicts(p, {"label": latex_names[sp]})
                else:
                    p = self._merge_dicts(p, {"label": sp})
            plots.append(plt.plot(x / xfactor, y, **p))

        if len(species) != 1:
            plt.legend()

        if "ylabel" not in kwargs:
            if len(species) != 1:
                plt.ylabel("Mass Fraction")
            else:
                if use_latex_names:
                    plt.ylabel("X(" + latex_names[species[0]] + ")")
                else:
                    plt.ylabel("X(" + species[0] + ")")

        if "xlabel" not in kwargs:
            plt.xlabel(prop)

        self.apply_class_methods(plt, kwargs)

        self.show_or_close(plt, kwargs)

    def plot_group_properties_vs_property(
        self,
        group,
        prop,
        props,
        xfactor=1,
        yfactor=None,
        rcParams=None,
        plotParams=None,
        **kwargs
    ):
        """Method to plot group mass fractions vs. zone property.

        Args:

            ``group`` (:obj:`str`): A string giving the group.

            ``prop`` (:obj:`str` or :obj:`tuple`): A string or tuple of
            up to three strings giving the property (which will
            serve as the plot abscissa).

            ``props`` (:obj:`list`): A list of strings or tuples of
            up to three strings giving the properties (which will
            serve as the plot ordinates).

            ``xfactor`` (:obj:`float`, optional): A float giving the scaling
            for the abscissa values.  Defaults to 1.

            ``yfactor`` (:obj:`float`, optional): A list of floats giving the scaling
            for the ordinate values.  Defaults to 1.

            ``rcParams``` (:obj:`dict`, optional): A dictionary of
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

        if yfactor:
            if len(yfactor) != len(props):
                print("yfactor length must be the same as the number of y properties.")
                return
        else:
            yfactor = np.full(len(props), 1.0)

        if plotParams:
            if len(plotParams) != len(props):
                print(
                    "Number of plotParam elements must equal" + " number of properties."
                )
                return

        x = self.get_group_properties_in_zones_as_floats(group, [prop])[prop]
        y = self.get_group_properties_in_zones_as_floats(group, props)

        for i, pr in enumerate(props):
            if plotParams is None:
                p = {}
            else:
                p = plotParams[i]
            if "label" not in p:
                p = self._merge_dicts(p, {"label": pr})
            plt.plot(x / xfactor, y[pr] / yfactor[i], **p)

        if "xlabel" not in kwargs:
            plt.xlabel(prop)

        if "ylabel" not in kwargs and len(props) == 1:
            plt.ylabel(props[0])

        if len(props) > 1:
            plt.legend()

        self.apply_class_methods(plt, kwargs)

        self.show_or_close(plt, kwargs)

    def plot_zone_mass_fractions_vs_property(
        self,
        zone,
        prop,
        species,
        xfactor=1,
        yfactor=None,
        use_latex_names=False,
        rcParams=None,
        plotParams=None,
        **kwargs
    ):
        """Method to plot zone mass fractions vs. zone property.

        Args:

            ``zone`` (:obj:`tuple`): A three element tuple giving the zone.

            ``prop`` (:obj:`str` or :obj:`tuple`): A string or tuple of
            up to three strings giving the property (which will
            serve as the plot abscissa).

            ``species`` (:obj:`list`): A list of strings giving the species
            to plot.

            ``xfactor`` (:obj:`float`, optional): A float giving the scaling
            for the abscissa values.  Defaults to 1.

            ``yfactor`` (:obj:`list`, optional): A list of floats giving
            factor by which to scale the mass fractions.  Defaults to not
            scaling.  If supplied, must by the same length as ``species``.

            ``use_latex_names`` (:obj:`bool`, optional): If set to True,
            species names converted to latex format.

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

        x = self.get_zone_properties_in_groups_as_floats(zone, [prop])[prop]
        m = self.get_zone_mass_fractions_in_groups(zone, species)

        if yfactor:
            if len(yfactor) != len(species):
                print("yfactor length must be the same as the number of species.")
                return
        else:
            yfactor = np.full(len(species), 1.0)

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
            plt.plot(x / xfactor, m[species[i]] / yfactor[i], **p)

        if len(species) != 1:
            plt.legend()

        if "ylabel" not in kwargs:
            if len(species) != 1:
                plt.ylabel("Mass Fraction")
            else:
                if use_latex_names:
                    plt.ylabel("X(" + latex_names[species[0]] + ")")
                else:
                    plt.ylabel("X(" + species[0] + ")")

        if "xlabel" not in kwargs:
            plt.xlabel(prop)

        self.apply_class_methods(plt, kwargs)

        self.show_or_close(plt, kwargs)

    def make_mass_fractions_movie(
        self,
        species,
        movie_name="",
        property=None,
        fps=15,
        xfactor=1,
        use_latex_names=False,
        title_func=None,
        rcParams=None,
        plotParams=None,
        **kwargs
    ):
        """Method to make a movie of mass fractions in the zones.

        Args:

            ``species`` (:obj:`list`): A list of the species to include
            in the movie.

            ``movie_name`` (:obj:`str`): A string giving the name of the
            resultin movie file.

            ``property`` (:obj:`str`, optional): A string giving property
            to be the x axis.  Defaults to zone index.

            ``fps`` (:obj:`float`, optional): A float giving the frames
            per second in the resulting movie.

            ``xfactor`` (:obj:`float`, optional): A float giving the
            scaling of the x axis.

            ``use_latex_names`` (:obj:`bool`, optional): If set to True,
            species names converted to latex format.

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
            seconds.

            ``rcParams`` (:obj:`dict`, optional): A dictionary of
            :obj:`matplotlib.rcParams` to be applied to the movie.
            Defaults to the default rcParams.

            ``plotParams`` (:obj:`list`, optional): A list of
            dictionaries of valid :obj:`matplotlib.pyplot.plot` optional
            keyword arguments to be applied to the lines in the movie.

            ``**kwargs``:  Acceptable :obj:`matplotlib.pyplot` functions.
            Include directly, as a :obj:`dict`, or both.

        Returns:
            The animation.

        """
        if plotParams:
            if len(plotParams) != len(species):
                print("Number of plotParam elements must equal" + " number of species.")
                return

        fig = plt.figure()

        self.set_plot_params(mpl, rcParams)

        nuclide_data = self.get_nuclide_data()

        groups = self.get_iterable_groups()

        if use_latex_names:
            latex_names = self.get_latex_names(species)

        def updatefig(i):
            fig.clear()
            x = self.get_group_mass_fractions(groups[i])
            for j, sp in enumerate(species):
                if plotParams is None:
                    p = {}
                else:
                    p = plotParams[j]
                if "label" not in p:
                    if use_latex_names:
                        p = self._merge_dicts(p, {"label": latex_names[sp]})
                    else:
                        p = self._merge_dicts(p, {"label": sp})
                if property:
                    p_prop = self.get_group_properties_in_zones_as_floats(
                        groups[i], [property]
                    )
                    plt.plot(
                        p_prop[property] / xfactor, x[:, nuclide_data[sp]["index"]], **p
                    )
                else:
                    plt.plot(x[:, nuclide_data[sp]["index"]], **p)

            if title_func:
                tf = title_func(i)
                if tf:
                    if isinstance(tf, tuple):
                        plt.title(tf[0], **tf[1])
                    elif isinstance(tf, str):
                        plt.title(tf)
                    else:
                        print("Invalid return from title function.")
                        return
            else:
                props = self.get_group_properties_in_zones_as_floats(
                    groups[i], ["time"]
                )
                plt.title(self.make_time_title_str(props["time"][0]))
            if "ylabel" not in kwargs:
                plt.ylabel("Mass Fraction")
            if "legend" not in kwargs:
                plt.legend()
            self.apply_class_methods(plt, kwargs)
            plt.draw()

        anim = animation.FuncAnimation(fig, updatefig, len(groups))
        if movie_name:
            anim.save(movie_name, fps=fps)

        return anim


class New_H5(wnb.Base):
    """A class for creating webnucleo hdf5 files.

       Each instance corresponds to new hdf5.  Main method sets group data.

       Args:
           ``file`` (:obj:`str`): A string giving the name of the new h5py\
            `file <https://docs.h5py.org/en/stable/high/file.html>`_.

           ``nucs`` (:obj:`dict`): A dictionary of nuclide data.

       """

    def __init__(self, file, nucs):
        self.file = h5py.File(file, "w")
        self.nucs = nucs
        self._add_nuclide_data(nucs)
        self.nuc_dict = {}

        i = 0
        for nuc in self.nucs:
            self.nuc_dict[nuc] = i
            i += 1

    def __del__(self):
        self.file.close()

    def _add_nuclide_data(self, nucs):
        dt = h5py.string_dtype()

        my_type = [
            ("Name", dt),
            ("index", "int"),
            ("Z", "int"),
            ("A", "int"),
            ("State", dt),
            ("Source", dt),
            ("Mass Excess", "float"),
            ("Spin", "float"),
        ]

        my_data = np.array([], dtype=my_type)

        i = 0
        for nuc in nucs:
            my_nuc = nucs[nuc]
            my_data = np.append(
                my_data,
                np.array(
                    (
                        nuc,
                        i,
                        my_nuc["z"],
                        my_nuc["a"],
                        my_nuc["state"],
                        my_nuc["source"],
                        my_nuc["mass excess"],
                        my_nuc["spin"],
                    ),
                    dtype=my_type,
                ),
            )
            i += 1

        self.file.create_dataset("Nuclide Data", data=my_data)

    def _add_zone_labels_to_group(self, g, zones):

        dt = h5py.string_dtype()

        my_type = [("Label 1", dt), ("Label 2", dt), ("Label 3", dt)]

        my_data = np.array([], dtype=my_type)

        for zone in zones:
            if type(zone) is tuple:
                tup = zone
            else:
                tup = (zone, "0", "0")
            my_data = np.append(
                my_data, np.array((tup[0], tup[1], tup[2]), dtype=my_type)
            )

        g.create_dataset("Zone Labels", data=my_data)

    def _add_zone_properties_to_group(self, g, zones):
        gp = g.create_group("Zone Properties")

        dt = h5py.string_dtype()

        my_type = [("Name", dt), ("Tag 1", dt), ("Tag 2", dt), ("Value", dt)]

        i = 0
        for zone in zones:
            my_data = np.array([], dtype=my_type)
            props = zones[zone]["properties"]
            for prop in props:
                name = str(prop[0])
                tag1 = "0"
                tag2 = "0"
                value = str(props[prop])
                if type(prop) is tuple:
                    name = str(prop[0])
                    tag1 = str(prop[1])
                    if len(prop) == 3:
                        tag2 = str(prop[2])
                else:
                    name = str(prop)
                my_data = np.append(
                    my_data, np.array((name, tag1, tag2, value), dtype=my_type)
                )
            gp.create_dataset(str(i), data=my_data, dtype=my_type)
            i += 1

    def _add_zone_mass_fractions_to_group(self, g, zones):
        dt = h5py.string_dtype()

        my_data = np.zeros((len(zones), len(self.nucs)), dtype=float)

        i = 0
        for zone in zones:
            mass_fracs = zones[zone]["mass fractions"]
            for key in mass_fracs:
                my_data[i][self.nuc_dict[key[0]]] = mass_fracs[key]
            i += 1

        g.create_dataset("Mass Fractions", data=my_data)

    def add_group(self, group, zones):
        """Method to add a group to an hdf5 file.

        Args:

            ``group`` (:obj:`str`): A string giving the group name.

            ``zones`` (:obj:`dict`): A dictionary of zone data for the group.

        Returns:
            On successful return, the group has been added to the
            hdf5 file.

        """

        g = self.file.create_group(group)

        self._add_zone_labels_to_group(g, zones)
        self._add_zone_properties_to_group(g, zones)
        self._add_zone_mass_fractions_to_group(g, zones)
