import wnutils.base as wb
import wnutils.h5 as w5
import matplotlib as mpl
import matplotlib.pyplot as plt


class Multi_H5(wb.Base):
    """A class for reading and plotting webnucleo multiple HDF5 files.

       Each instance corresponds to a set of HDF5 files.  Methods
       plot data from the files.

       Args:
           ``files`` (:obj:`list`): The names of the HDF5 files.

       """

    def __init__(self, files):
        self._files = files
        self._h5 = []
        for file in files:
            self._h5.append(w5.H5(file))

    def get_files(self):
        """Method to return the names of the input files.

        Returns:
            :obj:`list`:  A list of :obj:`str` giving the files

        """
        return self._files

    def get_h5(self):
        """Method to return individual H5 instances.

        Returns:
            :obj:`list`:  A list of individual :obj:`wnutils.h5.H5`
            instances.

        """
        return self._h5

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
        """Method to plot a property vs. a property in the files.

        Args:

            ``zone`` (:obj:`tuple`): A three-element :obj:`tuple` giving
            the three :obj:`str` labels of the zone.

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
            : obj: `matplotlib.rcParams` to be applied to the plot.
            Defaults to the default rcParams.

            ``plotParams`` (:obj:`list`, optional): A list of
            dictionaries of valid :obj:`matplotlib.pyplot.plot` optional
            keyword arguments to be applied to the plot.  The list must
            have the same number of elements number of files in the
            class instance.

            ``**kwargs``:  Acceptable: obj: `matplotlib.pyplot` functions.
            Include directly, as a :obj:`dict`, or both.

        Returns:
            A matplotlib plot.

        """

        self.set_plot_params(mpl, rcParams)

        h5s = self.get_h5()

        if plotParams:
            if len(h5s) != len(plotParams):
                print("Number of plot args must equal number of plots.")
                return

        for i, h5 in enumerate(h5s):
            result = h5.get_zone_properties_in_groups_as_floats(zone, [prop1, prop2])
            x = result[prop1] / xfactor
            y = result[prop2] / yfactor
            if plotParams:
                plt.plot(x, y, **plotParams[i])
            else:
                plt.plot(x, y)

        if "xlabel" not in kwargs:
            plt.xlabel(prop1)

        if "ylabel" not in kwargs:
            plt.ylabel(prop2)

        if "legend" not in kwargs:
            if plotParams:
                if "label" in plotParams[0]:
                    plt.legend()

        self.apply_class_methods(plt, kwargs)

        self.show_or_close(plt, kwargs)

    def plot_zone_mass_fraction_vs_property(
        self,
        zone,
        prop,
        species,
        xfactor=1,
        use_latex_names=False,
        rcParams=None,
        plotParams=None,
        **kwargs
    ):
        """Method to plot a mass fraction versus a property.

        Args:

            ``zone`` (:obj:`tuple`): A three-element :obj:`tuple` giving
            the three :obj:`str` labels of the zone.

            ``prop`` (:obj:`str` or :obj:`tuple`): A string or tuple
            of up to three strings giving the property (which will
            be the abscissa of the plot).

            ``species`` (:obj:`str`):  A string giving the species.

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
            have the same number of elements number of files in the
            class instance.


            ``**kwargs``:  Acceptable :obj:`matplotlib.pyplot` functions.
            Include directly, as a :obj:`dict`, or both.

        Returns:

            A matplotlib plot.

        """

        self.set_plot_params(mpl, rcParams)

        if use_latex_names:
            latex_names = self.get_latex_names([species])

        h5s = self.get_h5()

        if plotParams:
            if len(h5s) != len(plotParams):
                print("Number of plotParam elements must equal number of plots.")
                return

        for i, h5 in enumerate(h5s):
            x = h5.get_zone_properties_in_groups_as_floats(zone, [prop])[prop] / xfactor
            y = h5.get_zone_mass_fractions_in_groups(zone, [species])
            if plotParams:
                plt.plot(x, y[species], **plotParams[i])
            else:
                plt.plot(x, y[species])

        if "xlabel" not in kwargs:
            plt.xlabel(prop)

        if "ylabel" not in kwargs:
            if use_latex_names:
                s = "$X(" + latex_names[species][1:-1] + ")$"
            else:
                s = species
            plt.ylabel(s)

        if "legend" not in kwargs:
            if plotParams:
                if "label" in plotParams[0]:
                    plt.legend()

        self.apply_class_methods(plt, kwargs)

        self.show_or_close(plt, kwargs)
