Element-symbol utilities
========================

The :class:`wnutils.base.Base` class converts between atomic numbers and
element symbols.  Since the other wnutils classes inherit from ``Base``, the
same methods are available from XML and HDF5 objects.

Use :meth:`~wnutils.base.Base.get_element_symbol` to retrieve a symbol from an
atomic number::

    >>> import wnutils.base as wnb
    >>> base = wnb.Base()
    >>> base.get_element_symbol(29)
    'Cu'
    >>> base.get_element_symbol([18, 29, 120])
    ['Ar', 'Cu', 'Ubn']
    >>> base.get_element_symbol(29, lowercase=True)
    'cu'

Use :meth:`~wnutils.base.Base.get_atomic_number` for the reverse conversion.
Input symbols are case-insensitive::

    >>> base.get_atomic_number('Cu')
    29
    >>> base.get_atomic_number('cu')
    29
    >>> base.get_atomic_number(['Ar', 'cu', 'ubn'])
    [18, 29, 120]

Lists and tuples retain their container types.  NumPy arrays retain their
shape and are returned with object dtype so that temporary atomic numbers are
not restricted to a fixed-width integer type.

Temporary systematic symbols
----------------------------

For atomic numbers above 118, the methods generate and recognize systematic
temporary symbols.  The conversion has no artificial upper limit::

    >>> base.get_element_symbol(1220)
    'Ubbn'
    >>> base.get_atomic_number('uohbb')
    18622

These conversions apply the systematic symbol rules; they do not indicate
that an element exists or has received an official name.

Nitrogen and neutron notation
-----------------------------

Element symbols are case-insensitive, so both ``"N"`` and ``"n"`` mean
nitrogen in :meth:`~wnutils.base.Base.get_atomic_number` and return Z = 7.
The special interpretation of ``"n"`` as a neutron remains available when
parsing a *nuclide* name::

    >>> base.get_atomic_number('n')
    7
    >>> base.get_z_a_state_from_nuclide_name('n')
    (0, 1, '')

Invalid symbols, non-integral atomic numbers, and atomic numbers below one
raise an exception rather than returning a sentinel value.
