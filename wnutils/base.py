class Base:
    """Class for setting wnutils parameters and utilities."""

    def _get_property_name(self, tup):
        if len(tup) == 1:
            s = tup[0]
        elif len(tup) == 2:
            s = tup[0] + ", " + tup[1]
        elif len(tup) == 3:
            s = tup[0] + ", " + tup[1] + ", " + tup[2]
        else:
            s = "Invalid property name"

        return s

    def _merge_dicts(self, x, y):  # For Python 2
        z = x.copy()
        z.update(y)
        return z

    def show_or_close(self, plt, kwargs):
        """Method to show or close plot.

        Args:
            ``plt`` (:obj:`matplotlib.pyplot`): A pyplot plot instance.

            ``keyword_params`` (:obj:`dict`): A dictionary of functions that
            will be applied to the plot.  The key is the function and the
            value is the argument of the function.

        Returns:
            On successful return, the plot has been shown or closed.

        """

        if "show" in kwargs or "savefig" not in kwargs:
            plt.show()
        else:
            plt.close()

    def _class_comparator(self, k):
        if k == "show":
            return 2
        elif k == "savefig":
            return 1
        else:
            return 0

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

        for key in sorted(keyword_params, key=self._class_comparator):
            method = None

            try:
                method = getattr(plt, key)
            except AttributeError:
                raise NotImplementedError(
                    "Class `{}` does not implement `{}`".format(
                        plt.__class__.__name__, method
                    )
                )

            if isinstance(keyword_params[key], dict):
                method(**keyword_params[key])
            else:
                if isinstance(keyword_params[key], tuple):
                    method(keyword_params[key][0], **keyword_params[key][1])
                else:
                    method(keyword_params[key])

    def list_rcParams(self):
        """Method to list default rcParams.

        Returns:
            Prints the default :obj:`matplotlib.rcParams`.

        """

        import matplotlib as my_mpl

        print(my_mpl.rcParams.keys())

    def _get_species_name_substrings(self, str):
        b_read_elem = False
        b_read_mass = False
        elem = ""
        mass = ""
        state = ""
        for i in range(len(str)):
            if str[i].isalpha() and not b_read_elem:
                elem += str[i]
            elif str[i].isdigit() and not b_read_mass:
                mass += str[i]
                b_read_elem = True
            else:
                b_read_mass = True
                state += str[i]
        return (elem, mass, state)

    def _create_latex_string(self, str):
        l_hash = {
            "gamma": "\\gamma",
            "electron": "{\\rm e}^-",
            "positron": "{\\rm e}^+",
            "neutrino_e": "\\nu_e",
            "anti-neutrino_e": "{\\bar \\nu}_e",
            "neutrino_mu": "\\nu_\\mu",
            "anti-neutrino_mu": "{\\bar \\nu}_\\mu",
            "neutrino_tau": "\\nu_\\tau",
            "anti-neutrino_tau": "{\\bar \\nu}_\\tau",
        }

        if str in l_hash:
            return l_hash[str]
        else:
            str_T = self._get_species_name_substrings(str)
            elem = str_T[0]
            if str_T[1]:
                elem = str_T[0].title()
            if str_T[2]:
                return r"^{%s}\rm{%s}_{\rm{%s}}" % (str_T[1], elem, str_T[2])
            else:
                return r"^{%s}\rm{%s}" % (str_T[1], elem)

    def get_latex_names(self, nuclides):
        """Method to get latex strings of nuclides' names.

        Args:
            ``nuclides`` (:obj:`list`): A list of strings giving the nuclides.

        Returns:
            :obj:`dict`: A dictionary of latex strings.

        """

        latex_names = {}
        for nuclide in nuclides:
            name = r"$%s$" % (self._create_latex_string(nuclide))
            latex_names[nuclide] = name

        return latex_names

    def _create_zname_array(self):

        return [
            "n",
            "h",
            "he",
            "li",
            "be",
            "b",
            "c",
            "n",
            "o",
            "f",
            "ne",
            "na",
            "mg",
            "al",
            "si",
            "p",
            "s",
            "cl",
            "ar",
            "k",
            "ca",
            "sc",
            "ti",
            "v",
            "cr",
            "mn",
            "fe",
            "co",
            "ni",
            "cu",
            "zn",
            "ga",
            "ge",
            "as",
            "se",
            "br",
            "kr",
            "rb",
            "sr",
            "y",
            "zr",
            "nb",
            "mo",
            "tc",
            "ru",
            "rh",
            "pd",
            "ag",
            "cd",
            "in",
            "sn",
            "sb",
            "te",
            "i",
            "xe",
            "cs",
            "ba",
            "la",
            "ce",
            "pr",
            "nd",
            "pm",
            "sm",
            "eu",
            "gd",
            "tb",
            "dy",
            "ho",
            "er",
            "tm",
            "yb",
            "lu",
            "hf",
            "ta",
            "w",
            "re",
            "os",
            "ir",
            "pt",
            "au",
            "hg",
            "tl",
            "pb",
            "bi",
            "po",
            "at",
            "rn",
            "fr",
            "ra",
            "ac",
            "th",
            "pa",
            "u",
            "np",
            "pu",
            "am",
            "cm",
            "bk",
            "cf",
            "es",
            "fm",
            "md",
            "no",
            "lr",
            "rf",
            "db",
            "sg",
            "bh",
            "hs",
            "mt",
            "ds",
            "rg",
            "cn",
            "nh",
            "fl",
            "mc",
            "lv",
            "ts",
            "og",
        ]

    def _create_ex_name_array(self):
        return ["n", "u", "b", "t", "q", "p", "h", "s", "o", "e"]

    def _get_z_from_element_name(self, elem_str):
        s_zname = self._create_zname_array()

        if elem_str in s_zname:
            return s_zname.index(elem_str)
        else:
            ex_name = self._create_ex_name_array()
            result = ""
            for elem_char in elem_str:
                result += str(ex_name.index(elem_char))
            return int(result)

    def _create_element_name(self, z):

        s_zname = self._create_zname_array()

        ex_name = self._create_ex_name_array()

        elem_name = ""
        if z < len(s_zname):
            elem_name = s_zname[z]
        else:
            z_tmp = z
            while z_tmp:
                i = z_tmp % 10
                elem_name = ex_name[i] + elem_name
                z_tmp //= 10

        return elem_name

    def get_z_a_state_from_nuclide_name(self, name):
        """Method to get the Z, A, and state from the name of a nuclide.

        Args:
            ``name`` (:obj:`str`): The nuclide's name.

        Returns:
            A :obj:`tuple` containing the Z, A, and state label
            corresponding to the name.

        """

        elem, mass, state = self._get_species_name_substrings(name)

        if elem[0] == "n":
            if not mass:
                return (0, len(elem), state)
            else:
                if len(elem) == 1:
                    return (7, int(mass), state)

        return (int(self._get_z_from_element_name(elem)), int(mass), state)

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

        # Special cases

        if z == 0 and a == 1:
            return "n"
        elif z == 0 and a == 2:
            return "nn"

        # Normal cases

        name = self._create_element_name(z) + str(a) + state

        return name

    def make_time_t9_rho_title_str(self, props, i):
        """Method to create a default title string.

        Args:
            ``props`` (:obj:`dict`): A dictionary of :obj:`float`.
            The dictionary must contain entries that are
            :obj:`numpy.array` objects containing `time`, the time in seconds,
            `t9`, the temperature in billions of Kelvins, and
            `rho`, the mass density in grams per cubic centimeter.

            ``i`` (:obj:`int`): An integer giving the location in the
            arrays of the properties to use to construct the string.

        Returns:
            :obj:`str`: The default title string.

        """

        title_str = "time (s) = %8.2e, $T_9$ = %5.2f, rho (g/cc) = %8.2e" % (
            props["time"][i],
            props["t9"][i],
            props["rho"][i],
        )
        return title_str

    def make_time_title_str(self, time):
        """Method to create a default title string.

        Args:
            ``props`` (:obj:`dict`): A dictionary of :obj:`float`.
            The dictionary must contain at least one
            :obj:`numpy.array` object containing `time`, the time in seconds.

            ``time`` (:obj:`int`): A float giving the time
            to use to construct the string.

        Returns:
            :obj:`str`: The default title string.

        """

        title_str = "time (s) = %8.2e" % (time)
        return title_str
