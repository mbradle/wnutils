class Base:
    """Class for setting wnutils parameters and utilities."""

    def _get_property_name(self, tup):
        if(len(tup) == 1):
            s = tup[0]
        elif(len(tup) == 2):
            s = tup[0] + ', ' + tup[1]
        elif(len(tup) == 3):
            s = tup[0] + ', ' + tup[1] + ', ' + tup[2]
        else:
            s = 'Invalid property name'

        return s

    def _merge_dicts(self, x, y):    # For Python 2
        z = x.copy()
        z.update(y)
        return z

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

        for key in keyword_params:
            method = None

            try:
                method = getattr(plt, key)
            except AttributeError:
                raise NotImplementedError(
                    "Class `{}` does not implement `{}`".format(
                        plt.__class__.__name__, method_name
                    )
                )

            if isinstance(keyword_params[key], dict):
                method(**keyword_params[key])
            else:
                method(keyword_params[key])

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

    def create_nuclide_name(self, z, a, state):
        """Method to create the name of a nuclide.

        Args:
            ``z`` (:obj:`int`): An integer giving the nuclide's atomic
            number.

            ``a`` (:obj:`int`): An integer giving the nuclide's mass
            number.

            ``state`` (:obj:`str`): A string giving the nuclide's state
            suffix.

        Returns:
            :obj:`str`: The nuclide's name.

        """

        s_zname = ['n',
                   'h', 'he', 'li', 'be', 'b',
                   'c', 'n', 'o', 'f', 'ne',
                   'na', 'mg', 'al', 'si', 'p',
                   's', 'cl', 'ar', 'k', 'ca',
                   'sc', 'ti', 'v', 'cr', 'mn',
                   'fe', 'co', 'ni', 'cu', 'zn',
                   'ga', 'ge', 'as', 'se', 'br',
                   'kr', 'rb', 'sr', 'y', 'zr',
                   'nb', 'mo', 'tc', 'ru', 'rh',
                   'pd', 'ag', 'cd', 'in', 'sn',
                   'sb', 'te', 'i', 'xe', 'cs',
                   'ba', 'la', 'ce', 'pr', 'nd',
                   'pm', 'sm', 'eu', 'gd', 'tb',
                   'dy', 'ho', 'er', 'tm', 'yb',
                   'lu', 'hf', 'ta', 'w', 're',
                   'os', 'ir', 'pt', 'au', 'hg',
                   'tl', 'pb', 'bi', 'po', 'at',
                   'rn', 'fr', 'ra', 'ac', 'th',
                   'pa', 'u', 'np', 'pu', 'am',
                   'cm', 'bk', 'cf', 'es', 'fm',
                   'md', 'no', 'lr', 'rf', 'db',
                   'sg', 'bh', 'hs', 'mt', 'ds',
                   'rg', 'cn', 'nh', 'fl', 'mc',
                   'lv', 'ts', 'og'
                   ]

        ex_name = ['n', 'u', 'b', 't', 'q', 'p', 'h', 's', 'o', 'e']

        elem_name = ''
        if z <= len(s_zname):
            elem_name = s_zname[z]
        else:
            z_tmp = z
            while z_tmp:
                i = z_tmp % 10
                elem_name = ex_name[i] + elem_name
                z_tmp //= 10

        name = elem_name + str(a) + state

        return name
