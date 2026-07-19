from importlib.resources import files
from pathlib import Path

EXPECTED_SCHEMA_FILES = {
    "catalog",
    "input_nuclide_z_a.xsd",
    "libnucnet.xsd",
    "libnucnet__net.xsd",
    "libnucnet__nuc.xsd",
    "libnucnet__nuc__types.xsd",
    "libnucnet__reac.xsd",
    "libnucnet__reac__types.xsd",
    "xml.xsd",
    "zone_data.xsd",
    "zone_data_types.xsd",
    "README.md",
    "W3C_LICENSE.txt",
}


def test_all_vendored_schema_resources_are_available():
    schema_directory = files("wnutils") / "xsd_pub"

    for filename in EXPECTED_SCHEMA_FILES:
        assert (schema_directory / filename).is_file(), filename


def test_schema_provenance_matches_recorded_revision():
    repository_root = Path(__file__).parent.parent
    revision = (
        (repository_root / "XSD_REVISION").read_text(encoding="ascii").strip()
    )
    provenance = (
        repository_root / "wnutils" / "xsd_pub" / "README.md"
    ).read_text(encoding="utf-8")

    assert len(revision) == 40
    assert all(character in "0123456789abcdef" for character in revision)
    assert f"Upstream commit: `{revision}`" in provenance
