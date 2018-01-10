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

filename = "examples/base_empty.fits"

primary_hdu = hdulist[0]

# CREATE EVENTS data table HDU

print hdulist[1].columns

c_e_1 = Column(name = 'EVENT_ID', format = '1J', bscale = 1, bzero = 2147483648, array=np.array([]))
c_e_2 = Column(name = 'TIME',format = '1D', unit = 's', array=np.array([]))
c_e_3 = Column(name = 'RA',format = '1E', unit = 'deg', array=np.array([]))
c_e_4 = Column(name = 'DEC', format = '1E', unit = 'deg', array=np.array([]))
c_e_5 = Column(name = 'ENERGY', format = '1E', unit = 'TeV', array=np.array([]))
c_e_6 = Column(name = 'DETX', format = '1E', unit = 'deg', array=np.array([]))
c_e_7 = Column( name = 'DETY', format = '1E', unit = 'deg', array=np.array([]))
c_e_8 = Column(name = 'MC_ID', format = '1J', array=np.array([]))

coldefs = pyfits.ColDefs([c_e_1, c_e_2,c_e_3,c_e_4,c_e_5,c_e_6,c_e_7,c_e_8])

data_tbhdu = pyfits.BinTableHDU.from_columns(coldefs)
data_tbhdu.header = hdulist[1].header

gti_tstart = np.array([])
gti_tstop = np.array([])
c1 = Column(name='START', format='1D', array=gti_tstart)
c2 = Column(name='STOP', format='1D', array=gti_tstop)
coldefs = pyfits.ColDefs([c1, c2])
gti_tbhdu = pyfits.BinTableHDU.from_columns(coldefs)
gti_tbhdu.header = hdulist[2].header

thdulist = pyfits.HDUList([primary_hdu,data_tbhdu,gti_tbhdu])

if os.path.exists(filename):
    os.unlink(filename)
thdulist.writeto(filename)

hdulist_new = pyfits.open(filename)

print hdulist_new[1].data

hdulist_new.close()
hdulist.close()
