class WnBase:
    """Class for setting wnutils parameters and utilities."""

    def _get_property_name(self, tup):
        if(len(tup) == 1):
            s = tup[0]
        elif(len(tup) == 2):
            s = tup[0] + ',' + tup[1]
        elif(len(tup) == 3):
            s = tup[0] + ',' + tup[1] + ',' + tup[2]
        else:
            s = 'Invalid property name'

        return s

    def set_plot_params(self, my_mpl, my_params):
        """Method to set plot parameters.

        Args:
            ``my_mpl`` (matplotlib): A matplotlib instance.
            ``my_params`` (:obj:`dict`): A dictionary with rcParams to be
            applied.

        Returns:
            On successful return, the :obj:`matplotlib.rcParams` have first
            been set to their defaults and then updated with the values in
            my_params.

        """

        my_mpl.rcParams.update(my_mpl.rcParamsDefault)
        if my_params:
            for key in my_params:
                my_mpl.rcParams[key] = my_params[key]

    def apply_class_methods(self, plt, keyword_params):
        """Method to apply plot functions.

        Args:
            ``plt`` (:obj:`matplotlib.pyplot`): A pyplot plot instance.
            ``keyword_params`` (:obj:`dict`): A dictionary of functions that
            will be applied to the plot.  The key is the function and the
            value is the argument of the function.

        Returns:
            On successful return, the functions have been applied to the plot.

        """

        with_kwargs = ['legend']
        for key in keyword_params:
            if key not in with_kwargs:
                method = None

                try:
                    method = getattr(plt, key)
                except AttributeError:
                    raise NotImplementedError(
                        "Class `{}` does not implement `{}`".format(
                            plt.__class__.__name__, method_name
                        )
                    )

                method(keyword_params[key])

            elif key in with_kwargs:
                method = None

                try:
                    method = getattr(plt, key)
                except AttributeError:
                    raise NotImplementedError(
                        "Class `{}` does not implement `{}`".format(
                            plt.__class__.__name__, method_name
                        )
                    )

                for key2 in keyword_params[key]:
                    method(**{key2: keyword_params[key][key2]})

    def list_rcParams(self):
        """Method to list default rcParams.

        Returns:
            Prints the default :obj:`matplotlib.rcParams`.

        """

        import matplotlib as my_mpl
        print(my_mpl.rcParams.keys())

    def get_latex_names(self, nuclides):
        """Method to get latex strings of nuclides' names.

        Args:
            ``nuclides`` (:obj:`list`): A list of strings giving the nuclides.

        Returns:
            :obj:`dict`: A dictionary of latex strings.

        """

        latex_names = {}
        for nuclide in nuclides:
            if len(nuclide) != 1 or nuclide[0] != 'n':
                letters = nuclide[0].upper()
            else:
                letters = nuclide[0]
            numbers = ""
            for i in range(1, len(nuclide)):
                if nuclide[i].isalpha():
                    letters += nuclide[i]
                if nuclide[i].isdigit():
                    numbers += nuclide[i]
            name = r"$^{%s}\rm{%s}$" % (numbers, letters)
            latex_names[nuclide] = name

        return latex_names
