Changelog
=========

All notable changes to this project will be documented in this file.  This
project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`_.

Version 1.6.0
-------------

New:

  * A method to validate the XML against libnucnet schmeas has been added.

Fix:

  * State data is now parsed from XML correctly.
  * An error in creating IUPAC element names has been fixed.

Version 1.5.2
-------------

Fix:

  * The license attribute string has been shortened.
  * A typo in the tutorials has been fixed.

Version 1.5.1
-------------

Fix:

  * An error in constructing species names has been fixed.

Version 1.5.0
-------------

New:

  * State labels are now rendered as subscripts in species latex names.

Version 1.4.4
-------------

Fix:

  * The markdown indicator in setup.py has been fixed.

Version 1.4.3
-------------

Fix:

  * The XPath expressions in some routines have been fixed.

Version 1.4.2
-------------

Fix:

  * Nuclide naming for neutron and di-neutron has been fixed.

Version 1.4.1
-------------

Fix:

  * Storage for a single fit for a Non-Smoker rate entry has been fixed.

Version 1.4.0
-------------

New:

  * It is now possible to retrieve reaction data from webnucleo xml files
    and compute rates for standard rate functions.

Version 1.3.0
-------------

New:

  * It is now possible to set plot method arguments as a tuple giving an
    argument and a dictionary of optional keyword arguments.

Version 1.2.2
-------------

Fix:

  * An XPath error in an xml routine has been fixed.
  * A number of typos in the tutorials have been fixed.
  * The name of an h5 movie routine has been changed to better reflect its
    purpose.

Version 1.2.1
-------------

Fix:

  * A logical error in an h5 routine has been fixed.

Version 1.2.0
-------------

New:

  * Routines to create certain movies have been added.

Fix:

  * Some tutorial typos have been fixed and some missing text has been added.

Version 1.1.1
-------------

Internal:

  * An integer type error has been fixed.

Version 1.1.0
-------------

New:

  * The nuclear partition function data for each nuclide have been added to
    the nuclear data output.
  * It is now possible to retrieve the abundances of all nuclides in zones or
    a subset of zones in the xml namespace.
  * It is now possible to retrieve the network limits in the xml namespace.

Internal:

  * XPath selection of zones has been improved.

Version 1.0.0
-------------

New:

  * Initial release

