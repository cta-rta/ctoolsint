# ==========================================================================
# Main class for ctools integration into the Science Alert Generation system
#
# Copyright (C) 2018 Andrea Bulgarelli, Nicolò Parmiggiani, Simone Tampieri
#
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

from datetime import datetime
import os
import shutil
import gammalib
import ctools
import cscripts
from lxml import etree
import obsutils
from GammaPipeCommon.Configuration import ObservationConfiguration
from CTAGammaPipeCommon.create_fits import write_fits
from GammaPipeCommon.utility import Utility
from GammaPipeCommon.SkyImage import SkyImage
from conf import *
from math import ceil

#import CTA3GHextractor_wrapper

class DetectionOnOff:
	def __init__(self):
		return

	def init(self, obsfilename, simfilename, analysisfilename, runconf, eventfilename):
		self.obsfilename = obsfilename
		self.simfilename = simfilename
		self.analysisfilename = analysisfilename
		self.runconf = runconf
		self.eventfilename = eventfilename

		#print all attribute of a class
		#attrs = vars(self.runconf)
		#print(attrs)

		# Setup observations
		if self.obsfilename:
			self.obs = self.open_observation(self.obsfilename)

		if self.runconf:
			if self.runconf.skyframeref == 'fk5':
				print('pointing ra  ' + str(self.obsconf.point_ra) + ' dec ' + str(self.obsconf.point_dec) + ' frame ' + str(self.obsconf.point_frame))
				print('point roi ra ' + str(self.obsconf.roi_ra) + ' dec ' + str(self.obsconf.roi_dec) + ' frame ' + str(self.obsconf.roi_frame))
				print('run   roi ra ' + str(self.runconf.roi_ra) + ' dec ' + str(self.runconf.roi_dec) + ' frame ' + str(self.runconf.roi_frame))
			if self.runconf.skyframeref == 'galactic':
				print('pointing l  ' + str(self.obsconf.point_l) + ' b ' + str(self.obsconf.point_b) + ' frame ' + str(self.obsconf.point_frame))
				print('point roi l ' + str(self.obsconf.roi_l) + ' b ' + str(self.obsconf.roi_b) + ' frame ' + str(self.obsconf.roi_frame))
				print('run   roi l ' + str(self.runconf.roi_l) + ' b ' + str(self.runconf.roi_b) + ' frame ' + str(self.runconf.roi_frame))



		return

	def open_observation(self, obsfilename):

		print('Open observation')

		obs = gammalib.GObservations()

		self.obsconf = ObservationConfiguration(obsfilename, self.runconf.timesys, self.runconf.timeunit, self.runconf.skyframeref, self.runconf.skyframeunitref)
		print(self.obsconf.caldb)

		pntdir = gammalib.GSkyDir()

		in_pnttype = self.obsconf.point_frame
		print(in_pnttype)
		if in_pnttype == 'fk5' :
			pntdir.radec_deg(self.obsconf.point_ra, self.obsconf.point_dec)

		#if in_pnttype == 'equatorial' :
			#pntdir.radec_deg(self.obs_ra, self.obs_dec)

		#if in_pnttype == 'galactic' :
		#	pntdir.radec_deg(self.in_l, self.in_b)


		#pntdir.radec_deg(self.obsconf.obs_point_ra, self.obsconf.obs_point_dec)

		tstart = self.obsconf.tstart - self.runconf.timeref
		print(tstart)
		if self.runconf.timeref_timesys == 'mjd':
			tstart = tstart * 86400.

		print("TSTART " + str(tstart))

		obs1 = obsutils.set_obs(pntdir, tstart, self.obsconf.duration, 1.0, \
			self.obsconf.emin, self.obsconf.emax, self.obsconf.roi_fov, \
			self.obsconf.irf, self.obsconf.caldb, self.obsconf.id)

		print(obs1)

		obs.append(obs1)

		#print(obs1)
		return obs

	#rules
	#1) if simfilename perform simulation based on observation configuration. Do not select events based on run configuration
	#2) if eventfilename is present, read the file. Select events based on run configuration
	#3) if simfilename and eventfilename are not present, query the DB based on run and observation configuration

	#4) now that you have the event list in memory
	#4.A) make cts map
	#4.B) hypothesis generation (with spotfinders OR with the analysisfilename)
	#4.C) if you have an hypothesis, perform MLE

	def run_pipeline(self, debug=False, seed=0):
		"""
		Test unbinned pipeline with FITS file saving
		"""
		# Set script parameters
		events_name          = 'events.fits'
		cubefile_name 	     = ''
		selected_events_name = 'selected_events.fits'
		result_name          = 'results.xml'


		if self.simfilename and self.eventfilename:
			print('error')
			exit(10)

		############ Simulate events
    # in on-off analysis we need a shift on observation DEC coord

		if self.simfilename:

			# Setup simulation model
			self.obs.models(gammalib.GModels(self.simfilename))

			sim = ctools.ctobssim(self.obs)
			sim['debug'] = debug
			sim['seed']  = seed
			if self.runconf.WorkInMemory == 0:
				print('# Generate simulated event list on disk')
				# Simulate events on disk
				sim['outevents'] = events_name
				sim.execute()
				self.eventfilename = events_name

			if self.runconf.WorkInMemory == 1:
				print('# Generate simulated event list in memory')
				# Simulate events on memory
				sim.run()

			print("sim:", sim)
			print(sim.obs())

		#if self.runfilename is not present
		#   import into DB if any
		#	exit(0)

		############ Get events from DB

		if not self.simfilename and not self.eventfilename:
			#load from DB
			print('# Load event list from DB')

			#write selected_events_name
			if self.runconf.timeref_timesys == 'tt':
				tstart_tt = self.runconf.tmin
				tstop_tt = self.runconf.tmax
			if self.runconf.timeref_timesys == 'mjd':
				tstart_tt = Utility.convert_mjd_to_tt(self.runconf.tmin)
				tstop_tt = Utility.convert_mjd_to_tt(self.runconf.tmax)

			#tstart_tt = self.runconf.tmin
			#tstop_tt = self.runconf.tmax
			observationid = self.obsconf.id
			print("tstart"+str(tstart_tt))
			print("tstop"+str(tstart_tt))
			print(self.runconf.timeref_timesys)

			conf_dictionary = get_path_conf()

			path_base_fits = conf_dictionary['path_base_fits']
			tref_mjd = self.runconf.timeref

			if self.runconf.roi_frame == 'fk5':
				obs_ra = self.obsconf.roi_ra
				obs_dec = self.obsconf.roi_dec
			else:
				exit(10)

			emin = self.runconf.emin
			emax = self.runconf.emax
			fov = self.obsconf.roi_fov
			instrumentname = self.obsconf.instrument

			datarepository_dictionary = get_data_repository(instrumentname)
			datarepositoryid = datarepository_dictionary['datarepositoryid']

			print("before write fits")
			print(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])
			events_name = write_fits(tstart_tt,tstop_tt,observationid,datarepositoryid,path_base_fits, tref_mjd, obs_ra, obs_dec, emin, emax, 180, instrumentname)
			print("after write fits")
			print(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])


			print("fitsname"+events_name)
			if self.runconf.WorkInMemory == 2:
				print('# Load event list from disk')
				#Load events from fits file on memory
				sim = ctools.ctobssim(self.obs)
				events = sim.obs()[0].events()
				for event in events:
					print(event)

				#events.load(events_name)
				events.load(selected_events_name)

		############ Select events

		if self.runconf.WorkInMemory == 1:
			print('# Select event list in memory')
			select = ctools.ctselect(sim.obs())

		#using file
		if self.runconf.WorkInMemory == 0:
			print('# Select event list from disk: ', events_name)
			select = ctools.ctselect()
			select['inobs']  = events_name
			select['outobs'] = selected_events_name
			select['logfile'] = "ctselect.log"

		select['ra']     = self.runconf.roi_ra
		select['dec']    = self.runconf.roi_dec
		select['rad']    = self.runconf.roi_ringrad
		# select['tmin']   = 'MJD ' + str(self.runconf.tmin)
		# select['tmax']   = 'MJD ' + str(self.runconf.tmax)
		select['tmin']   = 'NONE'
		select['tmax']   = 'NONE'
		select['emin']   = self.runconf.emin
		select['emax']   = self.runconf.emax

		if self.runconf.WorkInMemory == 1:
			select.run()

		if self.runconf.WorkInMemory == 0:
			select.execute()

		print("after select events ", datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])

		print("select --")
		print(select)
		print("select --")
		print(select.obs())

		if self.runconf.WorkInMemory == 2:
			print('# Load event list from disk')
			#Load events from fits file on memory
			sim = ctools.ctobssim(self.obs)
			events = sim.obs()[0].events()
			for event in events:
				print(event)

			#events.load(events_name)
			events.load(selected_events_name)

		print('Event list generated ----------------------')
		if self.runconf.WorkInMemory == 0:
			print(self.obs)
			print("obs --")
			print(self.obs[0])
			print("obs 0 --")
			localobs = self.obs
			print("localobs:",localobs)

		if self.runconf.WorkInMemory == 1:
			print(select.obs())
			print(select.obs()[0])
			localobs = select.obs()

		for run in localobs:
			print('run ---'+selected_events_name)
			print(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])

			print("Run: ",run)

			# Create container with a single observation
			container = gammalib.GObservations()
			container.append(run)

			print(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])
			print(str(self.obsconf.caldb))

			# onoff analysis
			# get RA and DEC from analysisfilename
			xml_inmodel = etree.parse(self.analysisfilename)
			xml_get_coord = etree.XPath("./source/spatialModel/parameter[@name=$name]")

			phagen = cscripts.csphagen(select.obs())
			phagen['ebinalg']   = self.runconf.onoff_ebinalg
			phagen['emin']      = self.runconf.emin
			phagen['emax']      = self.runconf.emax
			phagen['rad']       = float(self.runconf.onoff_radius)
			phagen['ra']        = float(xml_get_coord(xml_inmodel, name='RA')[0].attrib.get('value'))
			phagen['dec']       = float(xml_get_coord(xml_inmodel, name='DEC')[0].attrib.get('value'))
			phagen['enumbins']  = int(self.runconf.onoff_enumbins)
			phagen['stack']     = False
			phagen['bkgmethod'] = self.runconf.onoff_bkgmethod
			phagen['coordsys']  = self.runconf.onoff_coordsys
			phagen['caldb']     = str(self.obsconf.caldb)
			phagen['irf']       = self.obsconf.irf
			phagen['outobs']    = 'onoff_obs.xml'
			phagen['prefix']    = 'csphagen'
			phagen['logfile']   = 'csphagen.log'
			if self.runconf.WorkInMemory == 0:
				phagen.execute()
			if self.runconf.WorkInMemory == 1:
				phagen.run()
			print(phagen)

			pha_obs_container = phagen.obs()
			print(pha_obs_container)

			#hypothesis builders
			#3GHextractor
			# 3GH Extractor code
			# if self.runconf.HypothesisGenerator3GH and cubefile_name:
			# 	self.analysisfilename = CTA3GHextractor_wrapper.extract_source(cubefile_name)
			# 	print(self.analysisfilename)
			# 	#cv2.waitKey(0)
			# 	print('HypothesisGeneratorEG3')

			#eseguire MLE
			print('analysisfilename: ' + self.analysisfilename)
			if self.analysisfilename:
				print('before MLE')
				print(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])

				# Perform maximum likelihood fitting

				# if self.runconf.WorkInMemory == 1:
				# 	like = ctools.ctlike(select.obs())

				# if self.runconf.WorkInMemory == 0:
				# 	like = ctools.ctlike()

				# 	if(self.runconf.binned == "1"):
				# 		like['inobs']  = cubefile_name
				# 		like['expcube'] = "NONE"
				# 		like['psfcube'] = "NONE"
				# 		like['edispcube'] = "NONE"
				# 		like['bkgcube'] = "NONE"
				# 		like['statistic'] = "CHI2"

				# 	if(self.runconf.binned == "0"):
				# 		like['inobs']  = selected_events_name
				# 		like['statistic'] = "DEFAULT"

				# we need the csphagen output observation file as input
				like = ctools.ctlike(phagen.obs())
				like['inobs']    = phagen['outobs'].value()
				like['inmodel']  = self.analysisfilename
				like['outmodel'] = result_name
				like['caldb']    = str(self.obsconf.caldb)
				like['irf']      = self.obsconf.irf

				like.execute()
				print(like)
				logL = like.opt().value()
				print(like.obs().models())


				print("after MLE")
				print(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])

				# insert logL into results.xml
				tree = etree.parse(result_name)
				contentnav = tree.find(".//source[@type='PointSource']")
				#contentdiv = contentnav.getparent()
				#contentnav.set("ts",str(logL))
				contentnav.set("runid",str(self.runconf.runid))
				#print(etree.tostring(tree,encoding="unicode",pretty_print=True))
				f = open(result_name, 'w')
				f.write(etree.tostring(tree,encoding="unicode",pretty_print=True))
				f.close()

				os.system('mkdir -p ' + self.runconf.resdir)
				shutil.copy('./results.xml', self.runconf.resdir + '/'+self.runconf.runprefix + '_results.xml')

				# if self.runconf.deleterun == "1":
				#	cmd = 'rm -r '+self.runconf.rundir
				#	os.system(cmd)

			# if self.runconf.HypothesisGenerator3GH:
			# 	CTA3GHextractor_wrapper.print_graphs(self.simfilename, result_name, self.analysisfilename)
			# 	#cv2.destroyAllWindows()
			# 	print('HypothesisGeneratorEG3')

		# Return
		return