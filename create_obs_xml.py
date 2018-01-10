# Copyright (c) 2017, AGILE team
# Authors: Nicolo' Parmiggiani <nicolo.parmiggiani@gmail.com>,
#
# Any information contained in this software is property of the AGILE TEAM
# and is strictly private and confidential. All rights reserved.

import os
import MySQLdb as mysql
import xml.etree.ElementTree as ET
from conf import get_conf



# create XML file whit obs informations
def create_obs_xml(obs_id,filename):

    # get configuration for connection
    conf_dictionary = get_conf()

    host = conf_dictionary['host']
    username = conf_dictionary['username']
    password = conf_dictionary['password']
    port = conf_dictionary['port']
    database = conf_dictionary['database']

    conn = mysql.connect(host,username,password,database)
    cursor = conn.cursor(mysql.cursors.DictCursor)

    #get observation info
    cursor.execute("select o.tstartreal,o.tendreal,o.lon,o.lat,ins.irf,ins.caldb,ins.fov,t.emin,t.emax from observation o join observation_target ot ON (ot.observationid = o.observationid) JOIN target t on(t.targetid = ot.targetid) join observingmode om ON (om.observingmodeid = t.observingmodeid) join instrument ins on (ins.instrumentid = om.instrumentid) where o.observationid = "+obs_id)

    row = cursor.fetchone()

    cursor.close()
    conn.close()

    in_l = str(row['lon'])
    in_b = str(row['lat'])
    in_tmin = str(row['tstartreal'])
    in_tmax = str(row['tendreal'])
    in_emin = str(row['emin'])
    in_emax = str(row['emax'])
    in_fov = str(row['fov'])
    in_irf = str(row['irf'])
    in_caldb = str(row['caldb'])

    #New time reference start from 51544.5
    in_tmin = str((float(in_tmin)-51544.5)*86400)
    in_tmax = str((float(in_tmax)-51544.5)*86400)

    #TODO Convert coordinate to ra,dec
    in_ra = in_l
    in_dec = in_b

    # create the structure
    data_observation = ET.Element('observation')
    pointing = ET.SubElement(data_observation, 'parameter')
    goodtimeintervals = ET.SubElement(data_observation, 'parameter')
    timereference = ET.SubElement(data_observation, 'parameter')
    regionofinterest = ET.SubElement(data_observation, 'parameter')
    deadtime = ET.SubElement(data_observation, 'parameter')
    calibration = ET.SubElement(data_observation, 'parameter')
    energy = ET.SubElement(data_observation, 'parameter')

    data_observation.set('name',"GPS")
    data_observation.set('id',obs_id)
    data_observation.set('instrument',"CTA")

    #Pointing
    pointing.set('name','Pointing')
    pointing.set('ra',in_ra)
    pointing.set('dec',in_dec)

    #GoodTimeIntervals
    goodtimeintervals.set('name','GoodTimeIntervals')
    goodtimeintervals.set('tmin',in_tmin)
    goodtimeintervals.set('tmax',in_tmax)

    # TimeReference
    timereference.set('name','TimeReference')
    timereference.set('mjdrefi','51544')
    timereference.set('mjdreff','0.5')
    timereference.set('timeunit','s')
    timereference.set('timesys','TT')
    timereference.set('timeref','LOCAL')

    # RegionOfInterest
    regionofinterest.set('name','RegionOfInterest')
    regionofinterest.set('ra',in_ra)
    regionofinterest.set('dec',in_dec)
    regionofinterest.set('rad',in_fov)

    #Deadtime
    deadtime.set('name','Deadtime')
    deadtime.set('deadc','1')

    #Calibration
    calibration.set('name','Calibration')
    calibration.set('database',in_caldb)
    calibration.set('response',in_irf)

    #Energy
    energy.set('name','Energy')
    energy.set('emin',in_emin)
    energy.set('emax',in_emax)

    #Write data
    data_observation_xml = ET.tostring(data_observation)
    file = open(filename, "w")
    file.write(data_observation_xml)


if __name__ == '__main__':

    # crete the XML for the specific observation
    obs_id = "1"
    filename = "/tmp/obs_"+obs_id+".xml"

    create_obs_xml(obs_id,filename)
