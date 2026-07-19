"""Utilities for working with webnucleo XML and HDF5 files."""

# Public attributes are populated dynamically by __getattr__.
# pylint: disable=undefined-all-variable

from importlib import import_module as _import_module

from wnutils.__about__ import (
    __author__,
    __copyright__,
    __summary__,
    __title__,
    __version__,
)

__all__ = [
    "Base",
    "H5",
    "Multi_H5",
    "Multi_Xml",
    "New_H5",
    "New_Xml",
    "Reaction",
    "Xml",
    "validate",
    "__author__",
    "__copyright__",
    "__summary__",
    "__title__",
    "__version__",
]

_LAZY_IMPORTS = {
    "Base": ("wnutils.base", "Base"),
    "H5": ("wnutils.h5", "H5"),
    "Multi_H5": ("wnutils.multi_h5", "Multi_H5"),
    "Multi_Xml": ("wnutils.multi_xml", "Multi_Xml"),
    "New_H5": ("wnutils.h5", "New_H5"),
    "New_Xml": ("wnutils.xml", "New_Xml"),
    "Reaction": ("wnutils.xml", "Reaction"),
    "Xml": ("wnutils.xml", "Xml"),
    "validate": ("wnutils.xml", "validate"),
}


def __getattr__(name):
    try:
        module_name, attribute_name = _LAZY_IMPORTS[name]
    except KeyError as error:
        raise AttributeError(
            f"module {__name__!r} has no attribute {name!r}"
        ) from error

    value = getattr(_import_module(module_name), attribute_name)
    globals()[name] = value
    return value


def __dir__():
    return sorted(set(globals()) | set(__all__))
