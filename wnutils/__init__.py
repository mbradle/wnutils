"""
A package of python routines to read and plot webnucleo xml and hdf5 files.
"""
import os

xml_catalog = os.path.join(os.path.dirname(__file__), "xsd_pub/catalog")

if "XML_CATALOG_FILES" in os.environ:
    os.environ["XML_CATALOG_FILES"] += " " + xml_catalog
else:
    os.environ["XML_CATALOG_FILES"] = xml_catalog

from wnutils.h5 import *
from wnutils.xml import *
from wnutils.multi_h5 import *
from wnutils.multi_xml import *
from wnutils.base import *
