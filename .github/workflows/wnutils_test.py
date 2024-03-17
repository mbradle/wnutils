import requests, io
import wnutils.xml as wx


def get_xml():
    xml = wx.Xml(
        io.BytesIO(requests.get("https://osf.io/kyhbs/download").content)
    )
    return xml

def test_validate():
    assert wx.validate(
        io.BytesIO(requests.get("https://osf.io/kyhbs/download").content)
    ) == None

def test_load():
    xml = get_xml()
    assert len(xml.get_nuclide_data()) > 0
    assert len(xml.get_reaction_data()) > 0

def test_nuclide():
    nucs = get_xml().get_nuclide_data(nuc_xpath="[z = 7]")
    s_nuc = 'n14'
    assert nucs[s_nuc]['z'] == 7
    assert nucs[s_nuc]['n'] == 7
    assert nucs[s_nuc]['a'] == 14
    assert len(nucs[s_nuc]['t9']) > 0
    assert len(nucs[s_nuc]['partf']) > 0

def test_reaction():
    reacs = get_xml().get_reaction_data(reac_xpath="[reactant = 'n' and product = 'gamma']")
    s_reac = 'n + fe56 -> fe57 + gamma'
    assert reacs[s_reac].get_string() == s_reac
    assert len(reacs[s_reac].reactants) > 0
    assert len(reacs[s_reac].nuclide_reactants) > 0
    assert len(reacs[s_reac].products) > 0
    assert len(reacs[s_reac].nuclide_products) > 0
    assert reacs[s_reac].compute_rate(1.) > 0

