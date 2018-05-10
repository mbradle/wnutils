def set_plot_params(mpl, keyword_params):
    mpl.rcParams.update(mpl.rcParamsDefault)
    if 'rcParams' in keyword_params:
        params = keyword_params['rcParams']
        for key in params:
            mpl.rcParams[key] = params[key]


def apply_class_methods(my_cls, keyword_params):
    excludes = ['use_latex_names', 'rcParams', 'x', 'y', 'xfactor']
    with_kwargs = ['legend']
    for key in keyword_params:
        if key not in excludes:
            if key not in with_kwargs:
                method = None

                try:
                    method = getattr(my_cls, key)
                except AttributeError:
                    raise NotImplementedError(
                        "Class `{}` does not implement `{}`".format(
                            my_cls.__class__.__name__, method_name
                        )
                    )

                method(keyword_params[key])

            elif key in with_kwargs:
                method = None

                try:
                    method = getattr(my_cls, key)
                except AttributeError:
                    raise NotImplementedError(
                       "Class `{}` does not implement `{}`".format(
                            my_cls.__class__.__name__, method_name
                       )
                    )

                for key2 in keyword_params[key]:
                    method(**{key2: keyword_params[key][key2]})


def list_rcParams():
    print(mpl.rcParams.keys())


