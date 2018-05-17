.. _installation:

Installing wnutils
=========================

First ensure that you have `pip <https://pip.pypa.io/en/stable/>`_
installed on your system by typing (at the command line prompt $)::

      $ pip --help

If this command does not return a proper usage statement,
install pip according to the instructions at the
pip `website <https://pip.pypa.io/en/stable/>`_.  Note that with python
version 3, you may have `pip3` instead of `pip`.

With pip installed, you may now use it to install wnutils by typing::

      $ pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple wnutils

..
      $ pip install wnutils

To test that wnutils has installed correctly, type::

      $ pip show wnutils

which should return information about the package.  To check that all
necessary packages are in place, open python by typing::

      $ python

or, perhaps for version 3::

      $ python3

and try importing wnutils by typing at the python prompt:

     >>> import wnutils

This command should simply return.  If not, there may be a message telling
you what packages your python installation is missing.  For example, on
some linux installations (particularly for python version 3),
we have had to install `python3-tk` via::

      $ sudo apt install python3-tk

In python version 2, that might be `python-tk`.  Of course, to exit python,
type::

     >>> exit()
