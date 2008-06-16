#!/usr/bin/env python

# This script creates the frozen version of Gnucleon, ie. the version
# with non-standard dependencies included. To do this we use bbfreeze
from bbfreeze import Freezer

# Our Freezer is given the directory we want the frozen version in and
# a list of the Python modules we want to include (these must be
# installed on any system running freeze.py)
f = Freezer('frozen', includes=('gtk', 'clutter', 'cairo'))

# Now we give it the Python code we want to freeze
f.addScript('gnucleon.py')

# Then we freeze it
f()

# Done!

