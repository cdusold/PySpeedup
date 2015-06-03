"""
.. moduleauthor:: Chris Dusold <PySpeedup@chrisdusold.com>

A module containing fast implementations of algorithms.

The motivation for this module was a mix between helper functions for Project
Euler solutions, and both in cryptography and discrete math investigations.

.. todo:: This is all either examples or to build up to the prime factorization
          class which I intend to build.

"""
from pyspeedup.algorithms._cached import cached
from pyspeedup.algorithms._fibonacci import fibonacci
from pyspeedup.algorithms._divideMod import divideMod
from pyspeedup.algorithms._invMod import invMod
from pyspeedup.algorithms._gcd import gcd
from pyspeedup.algorithms._legendre import jacobi_symbol
from pyspeedup.algorithms._squares import tsSquareRoot
from pyspeedup.algorithms._indexCalculus import discreteLog
from pyspeedup.algorithms._indexCalculus import rowReduce
from pyspeedup.algorithms._squares import isSquare
from pyspeedup.algorithms._factor import factor
import Primes as Primes