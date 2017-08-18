.. PySpeedup documentation master file, created by
   sphinx-quickstart on Sat Aug 16 17:10:37 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to PySpeedup's documentation!
=====================================

Contents:

.. toctree::
   :maxdepth: 2



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. include:: ../README.rst

Concurrent Module
=================

.. automodule:: pyspeedup.concurrent
   :members: __init__

Concurrent Buffer
-----------------

.. autoclass:: pyspeedup.concurrent.Buffer
.. autofunction:: pyspeedup.concurrent.buffer
.. autofunction:: pyspeedup.concurrent.uniformlyNonDecreasing
.. autofunction:: pyspeedup.concurrent.absolutelyNonDecreasing

Concurrent Cache
----------------

.. autoclass:: pyspeedup.concurrent.Cache

Algorithm Module
================

.. automodule:: pyspeedup.algorithms
   :members: __init__

   .. autofunction:: pyspeedup.algorithms.cached

   .. autofunction:: pyspeedup.algorithms.divideMod

   .. autofunction:: pyspeedup.algorithms.fibonacci(n)

   .. autofunction:: pyspeedup.algorithms.invMod

   .. autofunction:: pyspeedup.algorithms.gcd(a,b)

   .. autofunction:: pyspeedup.algorithms.jacobi_symbol(a,n)

   .. autofunction:: pyspeedup.algorithms.tsSquareRoot

   .. autofunction:: pyspeedup.algorithms.discreteLog

   .. autofunction:: pyspeedup.algorithms.rowReduce

   .. autofunction:: pyspeedup.algorithms.isSquare

   .. autofunction:: pyspeedup.algorithms.factor(N)

Memory Module
=============

.. automodule:: pyspeedup.memory
   :members: __init__

Disk Based Dictionary
---------------------

.. autoclass:: pyspeedup.memory.DiskDict

Ordered Access Disk Based Dictionary
---------------------

.. autoclass:: pyspeedup.memory.OrderedDiskDict

Disk Based List
---------------

.. autoclass:: pyspeedup.memory.DiskList
