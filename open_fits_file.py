# Copyright (c) 2017, AGILE team
# Authors: Nicolo' Parmiggiani <nicolo.parmiggiani@gmail.com>,
#
# Any information contained in this software is property of the AGILE TEAM
# and is strictly private and confidential. All rights reserved.

import pyfits
import numpy as np
from numpy import rec
from pyfits import Column
import os

hdulist = pyfits.open('examples/base.fits')

print hdulist[0].header

print hdulist[1].header
print hdulist[1].data
print hdulist[1].columns

hdulist.close()
