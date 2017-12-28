import os
import MySQLdb as mysql
import xml.etree.ElementTree as ET
from conf import get_conf

#get the observation informations from database
def get_info_from_db(obs_id):

    # get configuration for connection
    conf_dictionary = get_conf()

    host = conf_dictionary['host']
    username = conf_dictionary['username']
    password = conf_dictionary['password']
    port = conf_dictionary['port']
    database = conf_dictionary['database']

    conn = mysql.connect(host,username,password,database)
    cursor = conn.cursor(mysql.cursors.DictCursor)
    #get list of pipeline db
    cursor.execute("select o.tstartreal,o.tendreal-o.tstartreal as duration,o.lon,o.lat,ins.irf,ins.caldb,ins.fov,t.emin,t.emax from observation o join observation_target ot ON (ot.observationid = o.observationid) JOIN target t on(t.targetid = ot.targetid) join observingmode om ON (om.observingmodeid = t.observingmodeid) join instrument ins on (ins.instrumentid = om.instrumentid) where o.observationid = "+obs_id)

    row = cursor.fetchone()

    in_l = str(row['lon'])
    in_b = str(row['lat'])
    in_tstart = str(row['tstartreal'])
    in_duration = str(row['duration'])
    in_emin = str(row['emin'])
    in_emax = str(row['emax'])
    in_fov = str(row['fov'])
    in_irf = str(row['irf'])
    in_caldb = str(row['caldb'])

    obs_info = {'in_l':in_l,'in_b':in_b,'in_tstart':in_tstart,'in_duration':in_duration,
    'in_emin':in_emin,'in_emax':in_emax,'in_fov':in_fov,'in_irf':in_irf,'in_caldb':in_caldb}

    return obs_info

# create XML file whit obs informations
def create_obs_xml(obs_id,filename):

    # get info from database
    info_dictionary = get_info_from_db(obs_id)

    in_l = info_dictionary["in_l"]
    in_b = info_dictionary["in_b"]
    in_tstart = info_dictionary["in_tstart"]
    in_duration = info_dictionary["in_duration"]
    in_emin = info_dictionary["in_emin"]
    in_emax = info_dictionary["in_emax"]
    in_fov = info_dictionary["in_fov"]
    in_irf = info_dictionary["in_irf"]
    in_caldb = info_dictionary["in_caldb"]

    # create the structure
    data = ET.Element('data')
    observation = ET.SubElement(data, 'observation')
    target = ET.SubElement(data, 'target')
    instrument = ET.SubElement(data, 'instrument')

    #observation attribute
    observation.set('in_l',in_l)
    observation.set('in_b',in_b)
    observation.set('in_tstart',in_tstart)
    observation.set('in_duration',in_duration)
    observation.set('in_obsid',obs_id)

    #target attribute
    target.set('in_emin',in_emin)
    target.set('in_emax',in_emax)

    #instrument attribute
    instrument.set('in_fov',in_fov)
    instrument.set('in_irf',in_irf)
    instrument.set('in_caldb',in_caldb)

    # create XML file
    data_xml = ET.tostring(data)
    file = open(filename, "w")
    file.write(data_xml)


if __name__ == '__main__':

    # crete the XML for the specific observation
    obs_id = "1"
    filename = "/tmp/obs_"+obs_id+".xml"

    create_obs_xml(obs_id,filename)
