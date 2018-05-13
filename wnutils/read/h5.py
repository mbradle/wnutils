import warnings
with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=FutureWarning)
    import h5py

import numpy as np


def _get_group_zone_property_hash(file, group, zone_index):

    # Read HDF5 file

    h5file = h5py.File(file, 'r')

    properties = h5file['/' + group + '/Zone Properties/' + str(zone_index)]

    result = {}

    for property in properties:
        p0 = property[0].decode('ascii')
        p1 = property[1].decode('ascii')
        p2 = property[2].decode('ascii')
        name = ''
        if(p1 == '0' and p2 == '0'):
            name = p0
        elif(p1 != '0' and p2 == '0'):
            name = (p0, p1)
        else:
            name = (p0, p1, p2)
        result[name] = property[3].decode('ascii')

    return result


def _get_group_zone_labels_array(file, group):

    # Read HDF5 file

    h5file = h5py.File(file, 'r')
    zone_labels = h5file['/' + group + '/Zone Labels']

    result = []

    for i in range(len(zone_labels)):
        result.append(
            (
                zone_labels[i][0].decode('ascii'),
                zone_labels[i][1].decode('ascii'),
                zone_labels[i][2].decode('ascii')
            )
        )

    return result


def _get_group_zone_labels_hash(file, group):

    zone_labels_array = _get_group_zone_labels_array(file, group)

    result = {}

    for i in range(len(zone_labels_array)):
        result[zone_labels_array[i]] = i

    return result


def get_iterable_groups(file):
    """Function to return the non-nuclide data groups in a webnucleo hdf5 file.

    Args:
        ``file`` (:obj:`str`): The hdf5 file to be read.

    Returns:
        :obj:`list`: A list of strings giving the names of the groups.

    .. code-block:: python

       Example:

           import wnutils.read.h5 as w5
           groups = w5.get_iterable_groups('my_output.h5')
           for group in groups:
               print( group )

    """

    result = []

    # Read HDF5 file

    h5file = h5py.File(file, 'r')

    # Set data

    for group_name in h5file:
        if(group_name != 'Nuclide Data'):
            result.append(group_name)

    return result


def get_nuclide_data_array(file):
    """Function to return an array of nuclide data from a webnucleo hdf5 file.

    Args:
        ``file`` (:obj:`str`): The hdf5 file to be read.

    Returns:
        :obj:`list`: A list of the nuclide data.  Each
        entry is a dictionary containing the nuclide's index, name, z, a,
        source (data source), state, spin, and mass excess.

    .. code-block:: python

       Example:

           import wnutils.read.h5 as w5
           nuclides = w5.get_nuclide_data_array('my_output.h5')
           for nuclide in nuclides:
               print( nuclide['name'], " has spin ", nuclide['spin'] )

    """

    result = []

    # Read HDF5 file

    h5file = h5py.File(file, 'r')
    nuclide_data = h5file['/Nuclide Data']

    for i in range(len(nuclide_data)):
        data = {}
        data['name'] = nuclide_data[i][0].decode('ascii')
        data['z'] = nuclide_data[i][2]
        data['a'] = nuclide_data[i][3]
        data['source'] = nuclide_data[i][4].decode('ascii')
        data['state'] = nuclide_data[i][5].decode('ascii')
        data['spin'] = nuclide_data[i][6]
        data['mass excess'] = nuclide_data[i][7]
        result.append(data)

    return result


def get_nuclide_data_hash(file):
    """Function to return a nuclide data dictionary from a webnucleo hdf5 file.

    Args:
        ``file`` (:obj:`str`): The hdf5 file to be read.

    Returns:
        :obj:`dict`: A dictionary of the nuclide data.  Each
        entry is itself a dictionary containing the nuclide's index, name, z,
        a, source (data source), state, spin, and mass excess.

    .. code-block:: python

       Example:

           import wnutils.read.h5 as w5
           nuclides = w5.get_nuclide_data_hash('my_output.h5')
           print(
             " o16 has mass excess ", nuclides['o16']['mass excess'], " MeV"
           )

    """

    nuclide_data = get_nuclide_data_array(file)

    result = {}

    for i in range(len(nuclide_data)):
        data = {}
        data['index'] = i
        data['z'] = nuclide_data[i]['z']
        data['a'] = nuclide_data[i]['a']
        data['source'] = nuclide_data[i]['source']
        data['state'] = nuclide_data[i]['state']
        data['mass excess'] = nuclide_data[i]['mass excess']
        data['spin'] = nuclide_data[i]['spin']
        result[nuclide_data[i]['name']] = data

    return result


def get_group_mass_fractions(file, group):
    """Function to return mass fractions from a group in a webnucleo hdf5 file.

    Args:
        ``file`` (:obj:`str`): The hdf5 file to be read.

        ``group`` (:obj:`str`): The name of the group.

    Returns:
        :obj:`h5py:Dataset`: A 2d hdf5 dataset.  The first index indicates the
        species and the second the zone.

    .. code-block:: python

       Example:

           import wnutils.read.h5 as w5
           x = w5.get_group_mass_fractions('my_output.h5', 'Step 00001')
           nuclides = w5.get_nuclide_data_hash('my_output.h5')
           o16 = nuclides['o16']['index']
           for i in range(len(x)):
               print( x[i,o16] )

    """

    # Read HDF5 file

    h5file = h5py.File(file, 'r')
    return h5file['/' + group + '/Mass Fractions']


def get_zone_mass_fractions_in_groups(file, zone, nuclides):
    """Function to return zone mass fractions in all groups.

    Args:
        ``file`` (:obj:`str`): The hdf5 file to be read.

        ``zone`` (:obj:`tuple`): A three element tuple giving the three labels
        for the zone.

        ``nuclides`` (:obj:`list`): A list of strings giving the nuclides
        whose mass fractions are to be retrieved.

    Returns:
        :obj:`dict`: A dictionary of :obj:`numpy.array` giving the
        mass fractions in the groups.

    .. code-block:: python

       Example:

           import wnutils.read.h5 as w5
           x = w5.get_zone_mass_fractions_in_groups(
               'my_output.h5', ('1','0','0'), ['he4', 'c12', 'o16']
           )
           for i in range(len(x['o16'])):
               print( x['o16'][i] )

    """

    # Get index hash

    nuclide_hash = get_nuclide_data_hash(file)

    result = {}

    for nuclide in nuclides:
        result[nuclide] = np.array([])

    for group_name in get_iterable_groups(file):
        zone_index = _get_group_zone_labels_hash(file, group_name)
        x = get_group_mass_fractions(file, group_name)
        for nuclide in nuclides:
            result[nuclide] = np.append(
                result[nuclide],
                x[zone_index[zone], nuclide_hash[nuclide]['index']]
            )

    return result


def get_zone_properties_in_groups(file, zone, properties):
    """Function to return zone properties in all groups.

    Args:
        ``file`` (:obj:`str`): The hdf5 file to be read.

        ``zone`` (:obj:`tuple`): A three element tuple giving the three labels
        for the zone.

        ``properties`` (:obj:`list`): A list of strings giving the properties
        to be retrieved.

    Returns:
        :obj:`dict`: A dictionary of :obj:`list` giving the properties
        in the groups as strings.

    .. code-block:: python

       Example:

           import wnutils.read.h5 as w5
           x = w5.get_zone_properties_in_groups(
               'my_output.h5', ('1','0','0'), ['time', 't9']
           )
           for i in range(len(x['time'])):
               print( x['time'][i] )

    """

    # Get output

    result = {}

    for property in properties:
        result[property] = []

    for group_name in get_iterable_groups(file):
        zone_index = _get_group_zone_labels_hash(file, group_name)[zone]
        p = _get_group_zone_property_hash(file, group_name, zone_index)
        for property in properties:
            result[property].append(p[property])

    return result


def get_zone_properties_in_groups_as_floats(file, zone, properties):
    """Function to return zone properties in all groups as floats.

    Args:
        ``file`` (:obj:`str`): The hdf5 file to be read.

        ``zone`` (:obj:`tuple`): A three element tuple giving the three labels
        for the zone.

        ``properties`` (:obj:`list`): A list of strings giving the properties
        to be retrieved.

    Returns:
        :obj:`dict`: A dictionary of :obj:`numpy.array` giving the
        properties in the groups as floats.

    .. code-block:: python

       Example:

           import wnutils.read.h5 as w5
           x = w5.get_zone_properties_in_groups_as_floats(
               'my_output.h5', ('1','0','0'), ['time', 't9']
           )
           for i in range(len(x['time'])):
               print( x['time'][i] )

    """

    result = {}

    props = get_zone_properties_in_groups(file, zone, properties)

    for prop in props:
        result[prop] = np.array(props[prop], np.float_)

    return result


def get_group_properties_in_zones(file, group, properties):
    """Function to return properties in all zones for a group.

    Args:
        ``file`` (:obj:`str`): The hdf5 file to be read.

        ``group`` (:obj:`str`): A string giving the group name.

        ``properties`` (:obj:`list`): A list of strings giving the properties
        to be retrieved.

    Returns:
        :obj:`dict`: A dictionary of :obj:`list` giving the
        properties in the zones as strings.

    .. code-block:: python

       Example:

           import wnutils.read.h5 as w5
           x = w5.get_group_properties_in_zones(
               'my_output.h5', 'Step 00010', ['time', 't9']
           )
           for i in range(len(x['t9'])):
               print( x['time'][i] )

    """

    result = {}

    for property in properties:
        result[property] = []

    zone_labels_hash = _get_group_zone_labels_hash(file, group)

    for zone_labels in _get_group_zone_labels_array(file, group):
        p = (
            _get_group_zone_property_hash(
                file, group, zone_labels_hash[
                    (zone_labels[0], zone_labels[1], zone_labels[2])
                ]
            )
        )
        for property in properties:
            result[property].append(p[property])

    return result


def get_group_properties_in_zones_as_floats(file, group, properties):
    """Function to return properties in all zones for a group as floats.

    Args:
        ``file`` (:obj:`str`): The hdf5 file to be read.

        ``group`` (:obj:`str`): A string giving the group name.

        ``properties`` (:obj:`list`): A list of strings giving the properties
        to be retrieved.

    Returns:
        :obj:`dict`: A dictionary of :obj:`numpy.array` giving the
        properties in the zones as floats.

    .. code-block:: python

       Example:

           import wnutils.read.h5 as w5
           x = w5.get_group_properties_in_zones_as_floats(
               'my_output.h5', 'Step 00010', ['time', 't9']
           )
           for i in range(len(x['t9'])):
               print( x['time'][i] )

    """

    result = {}

    props = get_group_properties_in_zones(file, group, properties)

    for prop in props:
        result[prop] = np.array(props[prop], np.float_)

    return result
