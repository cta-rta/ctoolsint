# ==========================================================================
# Import detection results in database
#
# Copyright (C) 2018 Nicolo' Parmiggiani

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# ==========================================================================

import sys
from lxml import etree
from math import sqrt
from GammaPipeCommon.utility import *
from conf import get_pipedb_conf
import mysql.connector as mysql
import re
import time

import os
import subprocess


class ImportResults:

    def import_results(results_xml,check_alert):
        print("import"+str(results_xml))

        #read xml

        root_dir =  os.getcwd()

        conf_dictionary = get_pipedb_conf()

        pipedb_hostname = conf_dictionary['host']
        pipedb_username = conf_dictionary['username']
        pipedb_password = conf_dictionary['password']
        pipedb_port = conf_dictionary['port']
        pipedb_database = conf_dictionary['database']

        try:
            # get events list
            conn = mysql.connect(host=pipedb_hostname, user=pipedb_username, passwd=pipedb_password, db=pipedb_database)
            cursor = conn.cursor(dictionary=True)

            tree = etree.parse(results_xml)

            sources = tree.findall("//source")

            for source in sources:

                #for each point source
                if(source.attrib["type"]=="PointSource"):
                    print("source")

                    name = source.attrib["name"]

                    ts = source.attrib["ts"]
                    sqrtts = sqrt(float(ts))
                    print("sqrtts="+str(sqrtts))

                    runid = source.attrib["runid"]

                    spectrum_element = source.find("spectrum")
                    spectrum_type = spectrum_element.attrib["type"]
                    print("spectrum_type="+str(spectrum_type))


                    parameter_prefactor = spectrum_element.find("parameter[@name='Prefactor']")
                    flux = parameter_prefactor.attrib['value']
                    flux_err = parameter_prefactor.attrib['error']
                    flux_scale = parameter_prefactor.attrib['scale']

                    parameter_index = spectrum_element.find("parameter[@name='Index']")
                    spectral_index = parameter_index.attrib['value']
                    spectral_index_error = parameter_index.attrib['error']

                    spatial_model_element = source.find("spatialModel")
                    spatial_model_type = spatial_model_element.attrib['type']

                    parameter_ra = spatial_model_element.find("parameter[@name='RA']")
                    ra = parameter_ra.attrib['value']
                    ella = parameter_ra.attrib['error']

                    parameter_dec = spatial_model_element.find("parameter[@name='DEC']")
                    dec = parameter_dec.attrib['value']
                    ellb = parameter_dec.attrib['error']

                    ellphi = 0

                    #convert ra,dec to l,b
                    l,b = Utility.convert_fk5_to_gal(ra,dec)

                    #TODO
                    #check if already exist this detection

                    lpeak = -1
                    bpeak = -1
                    r = -1

                    query_run = "select tstart,tstop,emin,emax,l,b from run r join energybin eb ON (eb.energybinid = r.energybinid) where runid = "+runid
                    cursor.execute(query_run)
                    row= cursor.fetchone()

                    tstart = re.sub(r"\.0$", "", str(row['tstart']))
                    tstop = re.sub(r"\.0$", "", str(row['tstop']))
                    emin = re.sub(r"\.0$", "", str(row['emin']))
                    emax = re.sub(r"\.0$", "", str(row['emax']))
                    run_l = re.sub(r"\.0$", "", str(row['l']))
                    run_b = re.sub(r"\.0$", "", str(row['b']))

                    rootname = root_dir+"/T"+tstart+"_"+tstop+"_E"+emin+"_"+emax+"_P"+run_l+"_"+run_b

                    import_time = time.time()
            
                    #insert detection into DB and call alert algorithm
                    query_insert = ("insert into detection (rootname,label,runid,l,b,r,ella,ellb,ellphi,lpeak,bpeak,flux,fluxerr,sqrtts,spectralindex,spectralindexerr,import_time)"
                    " values ('"+str(rootname)+"','"+str(name)+"',"+str(runid)+","+str(l)+","+str(b)+",0,"+str(ella)+","+str(ellb)+","+str(ellphi)+","+str(lpeak)+","+str(bpeak)+","+str(flux)+""
                    ","+str(flux_err)+","+str(sqrtts)+","+str(spectral_index)+","+str(spectral_index_error)+","+str(import_time)+")")
                    print(query_insert)

                    cursor.execute(query_insert)
                    conn.commit()

                    detectionid = cursor.lastrowid
                    print("detectionid "+str(detectionid))


                    if(check_alert == 1):

                        #from run get tstart_tt tstop_tt
                        query = "select r.tstart,r.tstop,analysissessiontype_notice_observationid,analysissessiontype_observationid from run r join analysissession ans ON (ans.analysissessionid = r.analysissessionid) where runid = "+str(runid)
                        print(query)
                        cursor.execute(query)
                        run = cursor.fetchone()
                        t_start_tt = run['tstart']
                        t_stop_tt = run['tstop']
                        analysissessiontype_notice_observationid = run['analysissessiontype_notice_observationid']
                        analysissessiontype_observationid = run['analysissessiontype_observationid']

                        if analysissessiontype_notice_observationid is None:
                            analysissessiontype_notice_observationid = 'NULL'
                        if analysissessiontype_observationid is None:
                            analysissessiontype_observationid = 'NULL'

                        x_alert = 8
                        x_association = 4

                        cmd = "ruby $PIPELINE/GammaPipeCommon/alert/alert_check.rb "+str(detectionid)+" "+str(l)+" "+str(b)+" "+str(r)+" "+str(ella)+" "+str(ellb)+" "+str(ellphi)+" "+str(lpeak)+" "+str(bpeak)+" "+str(sqrtts)+" "+str(t_start_tt)+" "+str(t_stop_tt)+" "+str(analysissessiontype_observationid)+" "+str(analysissessiontype_notice_observationid)+" "+str(x_alert)+" "+str(x_association)+" "+str(root_dir)

                        output = subprocess.Popen(cmd,shell=True, stdout=subprocess.PIPE,stderr=subprocess.STDOUT).stdout.read().decode('utf-8')
                        print(output)

            if(check_alert == 1):

                #TODO gestione allerte doppie -> passare anche l'id della sessione per controllare solo quelle dove sono andato ad inserire
                cmd = "ruby $PIPELINE/GammaPipeCommon/alert/check_for_duplicate_alert.rb "+str(analysissessiontype_observationid)+" "+str(analysissessiontype_notice_observationid)

                output = subprocess.Popen(cmd,shell=True, stdout=subprocess.PIPE,stderr=subprocess.STDOUT).stdout.read().decode('utf-8')
                print(output)

            cursor.close()
            conn.close()

        except Exception as e :
            print(e)





if __name__ == '__main__':

    # Run binned in-memory pipeline
    ImportResults.import_results(sys.argv[1],sys.argv[2])
