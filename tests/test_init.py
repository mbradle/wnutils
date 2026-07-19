import importlib
import os
import subprocess
import sys

import wnutils


def test_plain_import_does_not_load_scientific_dependencies():
    code = """
import sys
import wnutils

for module in ("h5py", "matplotlib", "scipy", "wnutils.h5", "wnutils.xml"):
    assert module not in sys.modules, module
"""

    subprocess.run([sys.executable, "-c", code], check=True)


def test_top_level_public_api():
    assert wnutils.__version__ == "4.0.1"
    assert wnutils.__all__ == [
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

    for name in wnutils.__all__:
        assert hasattr(wnutils, name)


def test_dependency_names_are_not_exposed_at_top_level():
    for name in ("etree", "h5py", "mpl", "np", "os", "plt", "Real"):
        assert not hasattr(wnutils, name)


def test_import_does_not_modify_xml_catalog_environment(monkeypatch):
    monkeypatch.delenv("XML_CATALOG_FILES", raising=False)

    importlib.reload(wnutils)

    assert "XML_CATALOG_FILES" not in os.environ
