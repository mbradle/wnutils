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


def _get_zones(root, zone_xpath):
    return root.xpath('//zone' + zone_xpath)


def get_all_properties_in_zone(file, zone_xpath):

    zones = _get_zones(_get_root(file), zone_xpath)

    if len(zones) != 1:
        print("Select only one zone.")
        return None

    result = {}

    properties = zones[0].xpath('optional_properties/property')

    # Loop on properties

    for property in properties:
        result[property.xpath('@name')[0]] = property.text

    return result


def get_properties_in_zones(file, properties):
    """Function to return the properties in zones in an xml file

    Args:
        file (str): The name of the xml file.

    Returns:
        A dictionary of lists containing the properties in the zones
        as strings.

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

        path = '//zone_data/zone/optional_properties/property'

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


def get_properties_in_zones_as_floats(file, properties):
    """Function to return the properties in zones in an xml file

    Args:
        file (str): The name of the xml file.

    Returns:
        A dictionary of lists containing the properties in the zones
        as floats.

    """

    props = get_properties_in_zones(file, properties)

    dict = {}

    for prop in props:
        dict[prop] = np.array(list(map(float, props[prop])))

    return dict


def get_mass_fractions_in_zones(file, species, zone_xpath=""):
    """Function to retrieve mass fractions of species in the zones.

    Args:
        file (str): The name of the xml file.

        species (array): An array of strings giving the species whose mass fractions are to be retrieved.

        zone_xpath (str):  An XPath expression to select the zones.

    Returns:
        A dictionary of numpy arrays with the mass fractions for the requested
        species.

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
        result[my_species] = np.array(list(map(float, dict[my_species])))

    return result


def _get_zone(root, zone_name):

    if len(zone_name) == 1:
        result = root.xpath('//zone[@label1 = "%s"]' % zone_name[0])
    elif len(zone_name) == 2:
        result = root.xpath('zone[@label1 = "%s" and @label2 = %s]' %
                            zone_name[0], zone_name[1])
    elif len(zone_name) == 3:
        result = (
            root.xpath(
                'zone[@label1 = "%s" and @label2 = %s and @label3 = %s]' %
                zone_name[0], zone_name[1]
            )
        )

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


def get_abundances_vs_nucleon_number_in_zones(file, nucleon, zone_xpath):

    zones = _get_zones(_get_root(file), zone_xpath)

    result = []

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

        result.append( y )

    return result
