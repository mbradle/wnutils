from pathlib import Path

import numpy as np
import pytest

import wnutils.h5 as wh
import wnutils.multi_h5 as wm

H5_FILE = Path(__file__).parent / "data" / "small_network.h5"


@pytest.fixture
def h5_file():
    result = wh.H5(H5_FILE)
    yield result
    result.close()


def test_h5_context_manager_closes_file_after_exception():
    with pytest.raises(RuntimeError, match="fixture exception"):
        with wh.H5(H5_FILE) as h5_file:
            file_id = h5_file._h5file.id
            assert file_id.valid
            raise RuntimeError("fixture exception")

    assert not file_id.valid
    h5_file.close()


def test_new_h5_context_manager_closes_file(h5_file, tmp_path):
    output_path = tmp_path / "new.h5"

    with wh.New_H5(output_path, h5_file.get_nuclide_data()) as new_h5:
        file_id = new_h5.file.id
        assert file_id.valid

    assert not file_id.valid
    new_h5.close()


def test_multi_h5_context_manager_closes_all_files():
    with wm.Multi_H5([H5_FILE, H5_FILE]) as multi_h5:
        file_ids = [h5_file._h5file.id for h5_file in multi_h5.get_h5()]
        assert all(file_id.valid for file_id in file_ids)

    assert all(not file_id.valid for file_id in file_ids)
    multi_h5.close()


def test_multi_h5_closes_open_files_if_construction_fails(monkeypatch):
    opened_files = []

    class FakeH5:
        def __init__(self, file):
            if opened_files:
                raise OSError(f"Could not open {file}")
            self.closed = False
            opened_files.append(self)

        def close(self):
            self.closed = True

    monkeypatch.setattr(wm.w5, "H5", FakeH5)

    with pytest.raises(OSError, match="second.h5"):
        wm.Multi_H5(["first.h5", "second.h5"])

    assert opened_files[0].closed


def test_invalid_h5_plot_parameters_raise_exceptions(h5_file):
    with pytest.raises(ValueError, match="number of species"):
        h5_file.plot_group_mass_fractions(
            "step 0", ["h1"], plotParams=[{}, {}]
        )

    with wm.Multi_H5([H5_FILE, H5_FILE]) as multi_h5:
        with pytest.raises(ValueError, match="number of plots"):
            multi_h5.plot_zone_property_vs_property(
                ("0", "core", "0"), "time", "t9", plotParams=[{}]
            )


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
