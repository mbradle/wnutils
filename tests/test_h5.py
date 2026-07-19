from pathlib import Path

import numpy as np
import pytest

import wnutils.h5 as wh

H5_FILE = Path(__file__).parent / "data" / "small_network.h5"


@pytest.fixture
def h5_file():
    result = wh.H5(H5_FILE)
    yield result
    result._h5file.close()


def test_nuclide_metadata_uses_named_source_and_state_fields(h5_file):
    nuclides = h5_file.get_nuclide_data()

    assert nuclides["al26g"]["source"] == "wnutils test fixture"
    assert nuclides["al26g"]["state"] == "g"
    assert nuclides["al26m"]["state"] == "m"


def test_cached_nuclide_data_is_returned_as_a_defensive_copy(h5_file):
    first = h5_file.get_nuclide_data()
    first["h1"]["z"] = 99

    assert h5_file.get_nuclide_data()["h1"]["z"] == 1


def test_groups_labels_and_properties(h5_file):
    assert h5_file.get_iterable_groups() == ["step 0", "step 1"]
    assert h5_file.get_zone_labels_for_group("step 0") == [
        ("0", "core", "0"),
        ("1", "shell", "middle"),
        ("2", "shell", "outer"),
    ]

    properties = h5_file.get_group_properties_in_zones_as_floats(
        "step 1", ["time", ("rate scale", "weak")]
    )
    np.testing.assert_allclose(properties["time"], [3, 4, 5])
    np.testing.assert_allclose(
        properties[("rate scale", "weak")], [1.6, 1.8, 2.0]
    )


def test_batched_mass_fraction_lookup_across_groups(h5_file):
    result = h5_file.get_zone_mass_fractions_in_groups(
        ("1", "shell", "middle"), ["h1", "al26g", "al26m"]
    )

    np.testing.assert_allclose(result["h1"], [0.2, 0.15])
    np.testing.assert_allclose(result["al26g"], [0.1, 0.1])
    np.testing.assert_allclose(result["al26m"], [0.05, 0.1])
