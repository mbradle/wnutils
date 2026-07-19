from pathlib import Path

import numpy as np
import pytest

import wnutils.multi_xml as wm
import wnutils.xml as wx

XML_FILE = Path(__file__).parent / "data" / "small_network.xml"


def test_fixture_is_valid_libnucnet_input():
    assert wx.validate(XML_FILE) is None
    assert wx.Xml(XML_FILE).get_type() == "libnucnet_input"


def test_validation_uses_local_schemas_without_catalog_environment(
    monkeypatch,
):
    monkeypatch.delenv("XML_CATALOG_FILES", raising=False)

    assert wx.validate(XML_FILE) is None


def test_nuclide_data_includes_ground_and_metastable_states():
    nuclides = wx.Xml(XML_FILE).get_nuclide_data()

    assert set(nuclides) == {
        "n",
        "h1",
        "h2",
        "he4",
        "n14",
        "al26g",
        "al26m",
        "si27",
        "fe56",
        "fe57",
    }
    assert nuclides["n14"]["z"] == 7
    assert nuclides["n14"]["n"] == 7
    assert nuclides["al26g"]["state"] == "g"
    assert nuclides["al26m"]["state"] == "m"
    np.testing.assert_allclose(nuclides["al26g"]["t9"], [1, 2, 3])


def test_all_supported_reaction_representations_are_read():
    reactions = wx.Xml(XML_FILE).get_reaction_data()

    assert reactions["al26m -> al26g + gamma"].compute_rate(1.0) == 1.5
    assert reactions["n + fe56 -> fe57 + gamma"].compute_rate(1.0) > 0
    assert reactions["h1 + al26g -> si27 + gamma"].compute_rate(1.0) > 0

    user_reaction = reactions["h1 + al26m -> si27 + gamma"]
    rate = user_reaction.compute_rate(
        2.0, {"fixture user rate": lambda reaction, t9: t9 + 1}
    )
    assert rate == 3.0


def test_rate_table_accepts_real_number_scalars():
    reaction = wx.Xml(XML_FILE).get_reaction_data()["n + fe56 -> fe57 + gamma"]
    expected = reaction.compute_rate(1.0)

    assert reaction.compute_rate(1) == expected
    assert reaction.compute_rate(np.int64(1)) == expected


def test_reaction_rate_errors_raise_exceptions():
    user_reaction = wx.Xml(XML_FILE).get_reaction_data()[
        "h1 + al26m -> si27 + gamma"
    ]
    with pytest.raises(KeyError, match="fixture user rate"):
        user_reaction.compute_rate(1.0)

    reaction = wx.Reaction()
    reaction.data = {"type": "unsupported"}
    with pytest.raises(ValueError, match="Unsupported reaction type"):
        reaction.compute_rate(1.0)


def test_invalid_xml_queries_raise_exceptions():
    xml = wx.Xml(XML_FILE)

    with pytest.raises(ValueError, match="between one and three"):
        xml.get_properties([("name", "tag1", "tag2", "tag3")])
    with pytest.raises(KeyError, match="missing"):
        xml.get_properties(["missing"])
    with pytest.raises(ValueError, match="exactly one zone"):
        xml.get_all_properties_for_zone("")
    with pytest.raises(ValueError, match="nucleon"):
        xml.get_abundances_vs_nucleon_number("invalid")


def test_invalid_new_xml_operations_raise_exceptions():
    with pytest.raises(ValueError, match="Invalid XML type"):
        wx.New_Xml("invalid")

    with pytest.raises(ValueError, match="nuclear_data"):
        wx.New_Xml("zone_data").set_nuclide_data({})
    with pytest.raises(ValueError, match="reaction_data"):
        wx.New_Xml("nuclear_data").set_reaction_data({})
    with pytest.raises(ValueError, match="zone_data"):
        wx.New_Xml("nuclear_data").set_zone_data({})


def test_invalid_xml_plot_parameters_raise_exceptions():
    xml = wx.Xml(XML_FILE)
    with pytest.raises(ValueError, match="number of species"):
        xml.plot_mass_fractions_vs_property(
            "time", ["h1"], plotParams=[{}, {}]
        )

    multi_xml = wm.Multi_Xml([XML_FILE, XML_FILE])
    with pytest.raises(ValueError, match="number of plots"):
        multi_xml.plot_property_vs_property("time", "t9", plotParams=[{}])


def test_zone_properties_mass_fractions_and_abundances():
    xml = wx.Xml(XML_FILE)

    properties = xml.get_properties(["time", ("rate scale", "weak")])
    assert properties["time"] == ["0.0", "1.0", "2.0"]
    assert properties[("rate scale", "weak")] == ["1.0", "1.2", "1.4"]

    mass_fractions = xml.get_mass_fractions(["h1", "he4", "al26m"])
    np.testing.assert_allclose(mass_fractions["h1"], [0.5, 0.2, 0.1])
    np.testing.assert_allclose(mass_fractions["he4"], [0.25, 0.2, 0.1])
    np.testing.assert_allclose(mass_fractions["al26m"], [0.1, 0.05, 0.1])

    abundances = xml.get_all_abundances_in_zones()
    assert abundances.shape == (3, 27, 32)
    np.testing.assert_allclose(abundances[:, 1, 0], [0.5, 0.2, 0.1])
    np.testing.assert_allclose(
        abundances[:, 13, 13],
        [(0.15 + 0.1) / 26, (0.1 + 0.05) / 26, (0.2 + 0.1) / 26],
    )


def test_new_xml_round_trip_preserves_both_al26_states(tmp_path):
    source = wx.Xml(XML_FILE)
    output = tmp_path / "round_trip.xml"
    new_xml = wx.New_Xml("libnucnet_input")
    new_xml.set_nuclide_data(source.get_nuclide_data())
    new_xml.set_reaction_data(source.get_reaction_data())
    new_xml.set_zone_data(source.get_zone_data())
    new_xml.write(output)

    result = wx.Xml(output)
    nuclides = result.get_nuclide_data()
    assert nuclides["al26g"]["state"] == "g"
    assert nuclides["al26m"]["state"] == "m"
    assert set(result.get_reaction_data()) == set(source.get_reaction_data())
    assert result.get_zone_data().keys() == source.get_zone_data().keys()


def test_new_xml_rejects_over_tagged_properties():
    zones = {
        "0": {
            "properties": {("name", "tag1", "tag2", "tag3"): "value"},
            "mass fractions": {},
        }
    }
    with pytest.raises(ValueError, match="between one and three"):
        wx.New_Xml("zone_data").set_zone_data(zones)

    reaction = wx.Reaction()
    reaction.data = {
        "type": "user_rate",
        "key": "fixture",
        ("name", "tag1", "tag2", "tag3"): "value",
    }
    with pytest.raises(ValueError, match="between one and three"):
        wx.New_Xml("reaction_data").set_reaction_data({"fixture": reaction})
