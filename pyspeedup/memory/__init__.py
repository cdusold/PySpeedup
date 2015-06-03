"""
.. moduleauthor:: Chris Dusold <PySpeedup@chrisdusold.com>

A module containing storage classes that maintain small RAM usage and original structure access order.

The motivation for this module was to provide constant size RAM usage
while maintaining normal use of Python Dictionaries and possibly other
structures for semi-big data, where it isn't large enough to warrant more
big data centric solutions.

"""
from pyspeedup.memory._diskdict import DiskDict
from pyspeedup.memory._disklist import DiskList
from pyspeedup.memory._ordereddiskdict import OrderedDiskDict