"""
.. moduleauthor:: Chris Dusold <PySpeedup@chrisdusold.com>

A module containing fast implementations of algorithms.

The motivation for this module was a mix between helper functions for Project
Euler solutions, and both in cryptography and discrete math investigations.

.. todo:: This is all either examples or to build up to the prime factorization
          class which I intend to build.

"""
from _cached import cached
from _fibonacci import fibonacci
from _divideMod import divideMod
from _invMod import invMod
from _gcd import gcd
from _legendre import jacobi_symbol
from _squares import tsSquareRoot
from _indexCalculus import discreteLog
from _indexCalculus import rowReduce
from _squares import isSquare
from _factor import factor
