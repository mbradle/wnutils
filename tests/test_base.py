import numpy as np
import pytest

from wnutils.base import Base


@pytest.fixture
def base():
    return Base()


def test_get_element_symbol_for_official_and_temporary_elements(base):
    assert base.get_element_symbol(18) == "Ar"
    assert base.get_element_symbol(29) == "Cu"
    assert base.get_element_symbol(118) == "Og"
    assert base.get_element_symbol(120) == "Ubn"
    assert base.get_element_symbol(1220) == "Ubbn"
    assert base.get_element_symbol(18622) == "Uohbb"
    assert base.get_element_symbol(29, lowercase=True) == "cu"


def test_get_atomic_number_is_case_insensitive(base):
    assert base.get_atomic_number("Cu") == 29
    assert base.get_atomic_number("cu") == 29
    assert base.get_atomic_number("CU") == 29
    assert base.get_atomic_number("ubn") == 120
    assert base.get_atomic_number("Ubbn") == 1220
    assert base.get_atomic_number("uohbb") == 18622


def test_element_api_treats_n_as_nitrogen(base):
    assert base.get_element_symbol(7) == "N"
    assert base.get_atomic_number("N") == 7
    assert base.get_atomic_number("n") == 7
    assert base.get_z_a_state_from_nuclide_name("n") == (0, 1, "")


def test_list_and_tuple_container_types_are_preserved(base):
    assert base.get_element_symbol([18, 29, 120]) == ["Ar", "Cu", "Ubn"]
    assert base.get_atomic_number(("ar", "Cu", "UBN")) == (18, 29, 120)


def test_numpy_array_shape_is_preserved(base):
    atomic_numbers = np.array([[18, 29], [120, 1220]], dtype=object)
    symbols = base.get_element_symbol(atomic_numbers)

    assert symbols.dtype == object
    assert symbols.shape == atomic_numbers.shape
    assert symbols.tolist() == [["Ar", "Cu"], ["Ubn", "Ubbn"]]

    result = base.get_atomic_number(symbols)
    assert result.dtype == object
    assert result.shape == symbols.shape
    assert result.tolist() == atomic_numbers.tolist()


def test_arbitrarily_large_temporary_symbol_round_trip(base):
    atomic_number = int("1234567890" * 10)
    symbol = base.get_element_symbol(atomic_number)

    assert base.get_atomic_number(symbol) == atomic_number


@pytest.mark.parametrize("atomic_number", [0, -1])
def test_nonpositive_atomic_numbers_are_rejected(base, atomic_number):
    with pytest.raises(ValueError, match="positive"):
        base.get_element_symbol(atomic_number)


@pytest.mark.parametrize("atomic_number", [True, 29.0, "29", None])
def test_noninteger_atomic_numbers_are_rejected(base, atomic_number):
    with pytest.raises(TypeError, match="integers"):
        base.get_element_symbol(atomic_number)


@pytest.mark.parametrize(
    "symbol", ["", " Cu", "Cu2", "copper", "xyz", "nbn", "\N{KELVIN SIGN}"]
)
def test_invalid_element_symbols_are_rejected(base, symbol):
    with pytest.raises(ValueError, match="Invalid element symbol"):
        base.get_atomic_number(symbol)


def test_invalid_argument_types_are_rejected(base):
    with pytest.raises(TypeError, match="strings"):
        base.get_atomic_number(29)
    with pytest.raises(TypeError, match="boolean"):
        base.get_element_symbol(29, lowercase="yes")
