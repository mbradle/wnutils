from pathlib import Path

import matplotlib

matplotlib.use("Agg", force=True)
import matplotlib.pyplot as plt
import numpy as np
import pytest

import wnutils.h5 as wh
import wnutils.multi_h5 as wmh
import wnutils.multi_xml as wmx
import wnutils.xml as wx

DATA_DIRECTORY = Path(__file__).parent / "data"
H5_FILE = DATA_DIRECTORY / "small_network.h5"
XML_FILE = DATA_DIRECTORY / "small_network.xml"


def test_xml_and_multi_xml_plots_can_be_saved(tmp_path):
    xml_plot = tmp_path / "xml.png"
    wx.Xml(XML_FILE).plot_property_vs_property("time", "t9", savefig=xml_plot)
    assert xml_plot.is_file()

    multi_plot = tmp_path / "multi_xml.png"
    wmx.Multi_Xml([XML_FILE, XML_FILE]).plot_property_vs_property(
        "time", "t9", savefig=multi_plot
    )
    assert multi_plot.is_file()


def test_h5_and_multi_h5_plots_can_be_saved(tmp_path):
    zone = ("0", "core", "0")

    h5_plot = tmp_path / "h5.png"
    with wh.H5(H5_FILE) as h5_file:
        h5_file.plot_zone_property_vs_property(
            zone, "time", "t9", savefig=h5_plot
        )
    assert h5_plot.is_file()

    multi_plot = tmp_path / "multi_h5.png"
    with wmh.Multi_H5([H5_FILE, H5_FILE]) as multi_h5:
        multi_h5.plot_zone_property_vs_property(
            zone, "time", "t9", savefig=multi_plot
        )
    assert multi_plot.is_file()


def test_movie_rejects_curve_with_wrong_number_of_frames():
    extra_curves = [(np.arange(2), np.zeros((2, 2)))]

    try:
        with pytest.raises(ValueError, match="number of frames"):
            wx.Xml(XML_FILE).make_abundances_vs_nucleon_number_movie(
                extraCurves=extra_curves
            )
    finally:
        plt.close("all")
