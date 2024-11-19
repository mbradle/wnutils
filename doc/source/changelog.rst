Changelog
=========

All notable changes to this project will be documented in this file.  This
project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`_.

Version 3.1.1
--------------

Fix:

  * Float type has been adjust to be consistent with new NumPy standard.


Version 3.1.0
--------------

New:

  * Linting and testing have been added to the project integration.

Version 3.0.1
--------------

Fix:

  * The copy button requirement has been added to the package to enable proper
    documentation building.

Version 3.0.0
--------------

New:

  * Copy buttons have been added to the tutorial pages.

Fix:

  * XML validation has been moved out of the Xml class to a separate routine.
    This is a backwards-incompatible change.

Version 2.7.2
--------------

Fix:

  * A typo on the non-nuclide reaction element anti-neutrino_tau has been fixed.

Internal:

  * A build script has been added.

Version 2.7.1
--------------

Fix:

  * The XML write function no longer outputs zone mass fractions if they are
    zero.

Version 2.7.0
--------------

Internal:

  * Some string methods have been updated.  This means the package is no longer
    supported on Python 2.

New:

  * It is now possible to retrieve graphviz strings for nuclides.

Fix:

  * An extraneous and non-functioning search link has been removed.

Version 2.6.0
--------------

New:

  * The XML reaction class now contains lists of nuclide reactants and products     in addition to all reactants and product.
  * An Acknowledgments page has been added.
  * A link to the readthedocs page has been added for more visibility from PYPI     and GitHub.

Version 2.5.0
--------------

Internal:

  * Some Webnucleo links have been updated.
  * The validator now uses XML Catalog. The appropriate schema files are
    included in the distribution.

Version 2.4.0
--------------

Internal:

  * The documentation now uses a yaml file for readthedocs.

New:

  * It is now possible to plot zone properties versus a property for an HDF5
    group.

Version 2.3.1
--------------

Fix:

  * Zone labeling on output hdf5 has been fixed.
  * Some documentation typos have been fixed.

Version 2.3.0
--------------

New:

  * The capability to create new webnucleo hdf5 has been added.

Version 2.2.3
--------------

Fix:

  * Unneeded print method introduced in 2.2.0 removed since it caused
    documentation errors.

Version 2.2.2
--------------

Fix:

  * The tutorial data are now downloaded from OSF.

Version 2.2.1
--------------

Fix:

  * An error in assigning the atomic number of species starting with 'n'
    that was introduced in 2.2.0 has been fixed.

Version 2.2.0
--------------

New:

  * It is now possible to print out newly created XML files to the standard
    output.
  * The link to webnucleo has been updated.

Fix:

  * An ambiguity in retrieving atomic number, mass number, and state data from
    a nuclide with name 'n' (that is, neutron or nitrogen) has been fixed.

Version 2.1.0
--------------

New:

  * It is now possible to parse XML files with XInclude with wnutils.

Version 2.0.1
--------------

Fix:

  * A typo in a warning in the get_zone_data() routine has been fixed.

Version 2.0.0
--------------

New:

  * It is now possible to add fixed or time-dependent curves to the XML nucleon number and abundance chain movies.  The data are added via an array of tuples, which is a backwards incompatible change from the capability added in version 1.10.0.
  * The method to return chain abundances has been promoted to the API.

Fix:

  * The XML method to return all abundances in zones now returns the abundances for all species.

Version 1.10.2
--------------

Fix:

  * An error introduced in 1.10.1 in reading zone data has been fixed.

Version 1.10.1
--------------

Fix:

  * Parser now treats the nuclide name attribute in zone data as optional, as expected from the schema.

Version 1.10.0
--------------

New:

  * It is now possible to add extra curves to the XML nucleon number and abundance
    chain movies.
  * The animation tutorial has been updated to include information on the abundance
    chain movie and on adding extra curves.

Fix:

  * Parser now treats the reaction source as optional in the input XML file,
    as expected from the schema.
  * The assignment of mass number for abundance chain movies has been fixed.

Version 1.9.0
-------------

New:

  * A method to create an abundance chain movie has been added.
  * Movie routines now return the animation, and the movie file name is now an optional
    keyword. 

Fix:

  * Mis-assigments of spin and mass excess in the H5 class have been fixed.

Version 1.8.0
-------------

New:

  * A method to retrieve the root type of an Xml object has been added.
  * A method to retrieve zone data has been added.
  * A method to retrieve Z, A, and state label from a nuclide name
    has been added.
  * A link to code samples has been added.

Version 1.7.1
-------------

New:

  * A link to the tutorials in Jupyter notebook form has been added.

Fix:

  * Some tutorial typos have been fixed.

Version 1.7.0
-------------

New:

  * A new class allows the user to create webnucleo XML and write that XML
    to a file.

Fix:

  * The reaction rate calculator now computes the reaction rate from
    rate table data by not extrapolating from lowest and highest temperature
    values.  This means that, for temperatures below the lowest temperature
    in the table, the rate is computed at the lowest table temperature.
    Similarly, for temperatures above the highest temperature in the
    table, the rate is computed at the highest table temperature.  This
    treatment is in agreement with how libnucnet computes rates from rate
    tables.

Version 1.6.0
-------------

New:

  * A method to validate the XML against libnucnet schemas has been added.

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

