"""A convenience module for setting plot parameters and functions."""


def set_plot_params(my_mpl, my_params):
    """Function to set plot parameters.

    Args:
        ``my_mpl`` (matplotlib): A matplotlib instance.

        ``my_params`` (:obj:`dict`): A dictionary with rcParams to be
        applied.

    Returns:
        On successful return, the :obj:`matplotlib.rcParams` have first
        been set to their defaults and then updated with the values in
        my_params.

    Example:

        >>> import matplotlib as mpl
        >>> import wnutils as wn
        >>> params = {'lines.linewidth': 3, 'font.size': 14}
        >>> wn.params.set_plot_params( mpl, params )

    """

    if my_params:
        my_mpl.rcParams.update(my_mpl.rcParamsDefault)
        for key in my_params:
            my_mpl.rcParams[key] = my_params[key]


def apply_class_methods(plt, keyword_params):
    """Function to apply plot functions.

    Args:
        ``plt`` (:obj:`matplotlib.pyplot`): A pyplot plot instance.

        ``keyword_params`` (:obj:`dict`): A dictionary of functions that
        will be applied to the plot.  The key is the function and the value
        is the argument of the function.

    Returns:
        On successful return, the functions have been applied to the plot.

    Example:

        >>> import matplotlib.pyplot as plt
        >>> import wnutils as wn
        >>> keyword_params = {'ylim': [1.e-4,1], 'xlabel': 'time (s)'}
        >>> wn.params.apply_class_methods(plt, keyword_params)

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


def list_rcParams(my_mpl):
    """Function to list current rcParams.

    Args:
        ``my_mpl`` (matplotlib): A matplotlib instance.

    Returns:
        Prints the current :obj:`matplotlib.rcParams`.

    Example:

        >>> import matplotlib as mpl
        >>> import wnutils as wn
        >>> wn.params.list_rcParams(mpl)

    """
    print(my_mpl.rcParams.keys())
