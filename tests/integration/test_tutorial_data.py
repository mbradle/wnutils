import os
from pathlib import Path

import pytest

import wnutils.h5 as wh
import wnutils.xml as wx

DATA_DIRECTORY = os.environ.get("WNUTILS_TUTORIAL_DATA")
pytestmark = pytest.mark.skipif(
    DATA_DIRECTORY is None,
    reason="run through tests/integration/run_osf_tests.py",
)
DATA_DIR = Path(DATA_DIRECTORY or ".")


def test_large_tutorial_xml():
    path = DATA_DIR / "my_output1.xml"
    assert wx.validate(path) is None

    xml = wx.Xml(path)
    nuclides = xml.get_nuclide_data("[z = 7]")
    assert nuclides["n14"]["z"] == 7
    assert nuclides["n14"]["n"] == 7

    reaction = xml.get_reaction_data("[reactant = 'n' and product = 'gamma']")[
        "n + fe56 -> fe57 + gamma"
    ]
    assert reaction.compute_rate(1.0) > 0


def test_large_tutorial_h5():
    h5_file = wh.H5(DATA_DIR / "my_output1.h5")
    try:
        assert h5_file.get_nuclide_data()
        assert h5_file.get_iterable_groups()
    finally:
        h5_file._h5file.close()
