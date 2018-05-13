import numpy as np


def _get_root(file):
    from lxml import etree

    return etree.parse(file).getroot()


def _get_species_data(root):

    # Create output

    result = []

    # Get species

    species = root.xpath('//nuclear_data/nuclide')

    for sp in species:
        data = {}
        data['z'] = (sp.xpath('z'))[0].text
        data['a'] = (sp.xpath('a'))[0].text
        result.append(data)

    return result


def _get_species_data_for_zone(zone):

    # Create output

    result = {}

    # Get species

    species = zone.xpath('mass_fractions/nuclide')

    for sp in species:
        data = {}
        data['z'] = int((sp.xpath('z'))[0].text)
        data['a'] = int((sp.xpath('a'))[0].text)
        data['n'] = data['a'] - data['z']
        data['x'] = float((sp.xpath('x'))[0].text)
        result[sp.xpath('@name')[0]] = data

    return result


def _get_zones(root, zone_xpath):
    return root.xpath('//zone' + zone_xpath)


def _create_property_string(property):
    result = property.xpath('@name')[0]
    if(property.xpath('@tag1')):
        result += ', ' + property.xpath('@tag1')[0]
    if(property.xpath('@tag2')):
        result += ', ' + property.xpath('@tag2')[0]

    return result


def get_zone_properties(file, zone_xpath):
    """Function to return all properties of a single zone in an xml file

    Args:
        file (:obj:`str`): The xml file to be read.

        zone_xpath (:obj:`str`): XPath expression to select the single zone.

    Returns:
        :obj:`dict`: A dictionary containing the properties of the zone
        as strings.

    .. code-block:: python

       Example:

           import wnutils.read.xml as wx
           props = wx.get_zone_properties('my_output.xml', '[last()]' )
           for key in props:
               print( key, ':', props[key] )

    """

    zones = _get_zones(_get_root(file), zone_xpath)

    if len(zones) != 1:
        print("Select only one zone.")
        return None

    result = {}

    properties = zones[0].xpath('optional_properties/property')

    # Loop on properties

    for property in properties:
        result[_create_property_string(property)] = property.text

    return result


def get_properties_in_zones(file, properties, zone_xpath=' '):
    """Function to return the properties in zones in an xml file

    Args:
        file (:obj:`str`): The xml file to be read.

        properties (:obj:`list`): List of strings giving requested properites.

        zone_xpath (:obj:`str`, optional): XPath expression to select zones.
        Defaults to all zones.

    Returns:
        :obj:`dict`: A dictionary of lists containing the properties in the
        zones as strings.

    .. code-block:: python

       Example:

           import wnutils.read.xml as wx
           my_list = list( ('time','t9','rho') )
           props = wx.get_properties_in_zones('my_output.xml', my_list )
           print( props['t9'] )

    """

    root = _get_root(file)

    # Create properties tuple

    properties_t = {}

    for property in properties:
        if property.isalnum():
            properties_t[property] = (property,)
        else:
            properties_t[property] = (property.split(","))
            if len(properties_t[property]) > 3:
                print("\nToo many property tags (at most 2)!\n")
                exit()

    # Create output

    dict = {}

    for property in properties:
        dict[property] = []

    # Loop on properties

    for property in properties:

        tup = properties_t[property]

        path = '//zone' + zone_xpath + '/optional_properties/property'

        if len(tup) == 1:
            path += '[@name="%s"]' % tup[0].strip()
        elif len(tup) == 2:
            path += '[@name="%s" and @tag1="%s"]' % (
                tup[0].strip(), tup[1].strip())
        else:
            path += '[@name="%s" and @tag1="%s" and @tag2="%s"]' % (
                tup[0].strip(), tup[1].strip(), tup[2].strip())

        props = root.xpath(path)

        if len(props) == 0:
            print("Property not found.")
            return

        for elem in props:
            dict[property].append(elem.text)

    return dict


def get_properties_in_zones_as_floats(file, properties, zone_xpath=' '):
    """Function to return the properties in zones in an xml file

    Args:
        file (:obj:`str`): The xml file to be read.

        properties (:obj:`list`): List of strings giving requested properites.

        zone_xpath (:obj:`str`, optional): XPath expression to select zones.
        Defaults to all zones.

    Returns:
        :obj:`dict`: A dictionary of :obj:`numpy.array` containing the
        properties in the zones as floats.

    .. code-block:: python

       Example:

           import wnutils as wn
           props = wn.read.xml.get_properties_in_zones_as_floats(
               'my_output.xml', ['t9','rho'],
               zone_xpath='[position() > last() - 10]' # Get the last 10 zones
           )
           print( props['t9'] )
           print( type( props['rho'] ) )

    """

    props = get_properties_in_zones(file, properties, zone_xpath)

    dict = {}

    for prop in props:
        dict[prop] = np.array(props[prop], np.float_)

    return dict


def get_mass_fractions_in_zones(file, species, zone_xpath=' '):
    """Function to retrieve mass fractions of species in the zones.

    Args:
        file (:obj:`str`): The xml file to be read.

        species (:obj:`list`): List of strings giving requested species.

        zone_xpath (:obj:`str`, optional): XPath expression to select zones.
        Defaults to all zones.

    Returns:
        :obj:`dict`: A dictionary of :obj:`numpy.array` containing the mass
        fractions of the requested species in the zones as floats.

    .. code-block:: python

       Example:

           import wnutils.read.xml as wx
           x = wx.get_mass_fractions_in_zones(
               'my_output.xml', ['n','h1','he4','c12']
           )
           print( x['c12'] )

    """

    # Get the root.

    root = _get_root(file)

    # Create temporary hash

    dict = {}

    # Create output

    result = {}

    for my_species in species:
        dict[my_species] = []

    # Loop on zones

    zones = _get_zones(root, zone_xpath)

    for zone in zones:

        for my_species in species:

            data = zone.find(
                'mass_fractions/nuclide[@name="%s"]/x' % my_species)

            if data is None:
                dict[my_species].append(0.)
            else:
                dict[my_species].append(data.text)

    for my_species in species:
        result[my_species] = np.array(dict[my_species], np.float_)

    return result


def get_abundances_vs_nucleon_number_in_zones(
    file, nucleon='a', zone_xpath=' '
):
    """Function to retrieve abundances summed over nucleon number in zones.

    Args:
        file (:obj:`str`): The xml file to be read.

        nucleon (:obj:`str`): String giving the nucleon number to sum
        over.  Must be 'z', 'n', or 'a'.  Defaults to 'a'.

        zone_xpath (:obj:`str`, optional): XPath expression to select zones.
        Defaults to all zones.

    Returns:
        :obj:`numpy.array`: A two-dimensional :obj:`numpy.array` in which the
        first index gives the zone and the second gives the nucleon number
        value.

    .. code-block:: python

       Example:

           import wnutils.read.xml as wx
           y = wx.get_abundances_vs_nucleon_number_in_zones(
               'my_output.xml', nucleon='z'
           )
           for i in range(y.shape[1]):
               print( 'Z =', i, ', Y(Z) = ', y[10,i] )  # Abundances of zone 11

    """

    if(nucleon != 'z' and nucleon != 'n' and nucleon != 'a'):
        print("nucleon must be 'z', 'n', or 'a'.")
        return

    zones = _get_zones(_get_root(file), zone_xpath)

    result = np.array([])

    for zone in zones:

        # Get species data

        sp = _get_species_data_for_zone(zone)

        # Determine output array

        n = []

        for s in sp:
            n.append(sp[s][nucleon])

        y = [0.] * (max(n) + 1)

        for s in sp:
            y[sp[s][nucleon]] += sp[s]['x'] / sp[s]['a']

        if(result.size == 0):
            result = np.append(result, y)
        else:
            result = np.vstack([result, y])

    return result
