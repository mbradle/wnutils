"""A set of utility routines for wnutils."""


def get_latex_names(nuclides):
    """Function to get latex strings of nuclides' names.

    Args:
        ``nuclides`` (:obj:`list`): A list of strings giving the nuclides.

    Returns:
        :obj:`dict`: A dictionary of latex strings.

    .. code-block:: python

       Example:

           import wnutils as wn
           nuclides = ['n', 'n14', 'o16', 'u238']
           lnames = wn.utils.get_latex_names( nuclides )
           for key in lnames:
               print( key, ":", lnames[key] )

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
