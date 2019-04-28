import cscripts
import ctools
import gammalib
import logging
import obsutils
import os
import shutil
import xml.etree.ElementTree as ET
from conf import * # get_path_conf, get_data_repository
from math import ceil
from CTAGammaPipeCommon.create_fits import write_fits # DB connection
from PipeConfiguration import ObservationConfiguration
from GammaPipeCommon.utility import Utility
from GammaPipeCommon.SkyImage import SkyImage

# FIXME doubts
# * simulation from observation (obs.xml) or not?
# * load events from db: we don't use fov. is it right?
#                        workInMemory == 2 ? what expected from events.load() ?
# * events filename are good for input and output. maybe we can distinguish them
class Detection:
	DEFAULT_EVENTS_FILE   = 'events.fits'
	DEFAULT_SELECTED_FILE = 'selected_events.fits'
	DEFAULT_CUBECNT_FILE  = 'cube.fits'
	DEFAULT_RESULTS_FILE  = 'results.xml'
	DEFAULT_ONOFF_OBS_FILE = 'onoff_obs.xml'

	def __init__(self, args):
		self.obsfilename      = args['obsfilename']
		self.simfilename      = args['simfilename']
		self.analysisfilename = args['analysisfilename']
		self.eventfilename    = args['eventfilename']
		self.runconf          = args['runconf']

		self.events_file  = self.eventfilename or self.DEFAULT_EVENTS_FILE
		self.selected_events_file = self.DEFAULT_SELECTED_FILE
		self.cube_file    = self.DEFAULT_CUBECNT_FILE
		self.results_file = self.DEFAULT_RESULTS_FILE
		self.onoff_obs_file = self.DEFAULT_ONOFF_OBS_FILE

		self.obs = None
		self.obsconf = None

		if self.obsfilename:
			self.obsconf = ObservationConfiguration(self.obsfilename, self.runconf.timesys, self.runconf.timeunit, self.runconf.skyframeref, self.runconf.skyframeunitref)
			self.obs = self.create_observation(obsconf=self.obsconf, ref_timestart=self.runconf.timeref, ref_timesys=self.runconf.timeref_timesys)
			if self.simfilename:
				self.obs.models(self.simfilename)

		return
		# show observation info
		logging.debug(self.obs)
		for cta_o in self.obs:
			logging.debug(cta_o)
			logging.debug('CTA Observation events:\n%s' % cta_o.events().gti())
		for model in self.obs.models():
			logging.debug(model)

		if self.runconf:
			if self.runconf.skyframeref == 'fk5':
				logging.info('pointing  ra %s, dec %s, frame %s', str(self.obsconf.point_ra), str(self.obsconf.point_dec), str(self.obsconf.point_frame))
				logging.info('point roi ra %s, dec %s, frame %s', str(self.obsconf.roi_ra), str(self.obsconf.roi_dec), str(self.obsconf.roi_frame))
				logging.info('run   roi ra %s, dec %s, frame %s', str(self.runconf.roi_ra), str(self.runconf.roi_dec), str(self.runconf.roi_frame))
			elif self.runconf.skyframeref == 'galactic':
				logging.info('pointing  l %s, b %s, frame %s', str(self.obsconf.point_l), str(self.obsconf.point_b), str(self.obsconf.point_frame))
				logging.info('point roi l %s, b %s, frame %s', str(self.obsconf.roi_l), str(self.obsconf.roi_b), str(self.obsconf.roi_frame))
				logging.info('run   roi l %s, b %s, frame %s', str(self.runconf.roi_l), str(self.runconf.roi_b), str(self.runconf.roi_frame))
		return

	def create_observation(self, obsconf=None, ref_timestart=None, ref_timesys=None):
		"""
		Return a GObservation observation container
		Parameters:
		. obsconf : observation xml configuration
		. ref_timestart : science tool reference timestart
		. ref_timesys   : science tool reference timesystem
		"""
		if not obsconf or not ref_timestart or not ref_timesys:
			logging.error("Cannot create an observation without obsconf and science tool timestart or timesys")
			exit(1)

		pntdir = gammalib.GSkyDir()
		if obsconf.point_frame == 'fk5':
			pntdir.radec_deg(obsconf.point_ra, obsconf.point_dec)
	
		# obsconf.tstart = observation[GoodTimeIntervals][tstartreal] (days)
		# ref_timestart = run[ScienceToolReference][timestart] (days)
		#    GTime ref: http://cta.irap.omp.eu/gammalib/users/user_manual/modules/obs.html#sec-time
		tstart = obsconf.tstart - ref_timestart
		logging.info('tstart diff: %s (days)' % str(tstart))
		if ref_timesys == 'mjd':
			tstart = tstart * 86400.0
			logging.info('TSTART: %s (sec)' % str(tstart))
		else:
			logging.warn("ScienceToolReference time system is not MJD [%s]. Please, check the events start time." % ref_timesys)

		# obsutils.set_obs need tstart and duration in seconds
		cta_obs = obsutils.set_obs(pntdir, tstart=tstart, duration=obsconf.duration, deadc=1.0, \
			emin=obsconf.emin, emax=obsconf.emax,   rad=obsconf.roi_fov, \
			irf=obsconf.irf,   caldb=obsconf.caldb, obsid=obsconf.id)

		obs = gammalib.GObservations()
		obs.append(cta_obs)
		return obs

	def run_pipeline(self, debug=False, seed=0):
		in_memory = self.runconf.WorkInMemory
		onoff_analysis = self.runconf.onoff_analysis

		starting_obs = self.get_starting_observations(debug=debug, seed=seed, in_memory=in_memory)
		selection = self.select_events(starting_obs, self.runconf, output_file=self.selected_events_file, in_memory=in_memory)
		gobservations = selection.obs()

		if self.runconf.MakeCtsMap == 1:
			binned_obs = self.generate_counts_cube(gobservations, in_memory=in_memory)
			gobservations = binned_obs # replace selected obs with binned obs

		# onoff vs countsmap priority
		if onoff_analysis:
			pha_obs = self.generate_onoff_observation(gobservations, in_memory=in_memory)
			gobservations = pha_obs

		if self.analysisfilename:
			self.execute_likelihood(gobservations, binned=int(self.runconf.binned), onoff_analysis=onoff_analysis, in_memory=in_memory)

		return

	def get_starting_observations(self, debug=False, seed=0, in_memory=0):
		"""
		Return a GObservations object with events.
		"""
		obs = None

		if self.simfilename and self.eventfilename:
			logging.error('Cannot works with simfilename && eventfilename')
			exit(10)
		elif self.simfilename:
			simulation = self.create_events_simulation(debug=debug, seed=seed, in_memory=in_memory, model=self.simfilename, events_output=self.events_file, conf=self.obsconf)
			obs = simulation.obs() # GObservation
		elif self.eventfilename:
			cta_obs = gammalib.GCTAObservation(self.eventfilename)
			obs = gammalib.GObservations()
			obs.append(cta_obs)
		elif not self.simfilename and not self.eventfilename:
			# TODO Not tested
			db_events_file = self.load_events_from_db()
			cta_obs = gammalib.GCTAObservation(db_events_file)
			obs = gammalib.GObservations()
			obs.append(cta_obs)
		else:
			logging.error('Unmanaged condition')
			exit(11)

		logging.debug('=== post simulation ===')
		logging.debug(obs)                   # GObservations
		logging.debug(obs[0])                # GCTAObservation
		logging.debug(obs[0].events())       # GCTAEventList
		logging.debug(obs[0].events().gti()) # GGti

		# .clone() to avoid annoying errors while object is destructing.
		return obs.clone()

	@staticmethod
	def create_events_simulation(debug=False, seed=0, in_memory=0, model=None, events_output=None, conf={}):
		"""
		Return a ctobssim GApplication using the simulation model filename as inmodel.
		"""
		sim = ctools.ctobssim()
		sim['inmodel']   = model
		sim['outevents'] = events_output
		sim['debug'] = debug
		sim['seed']  = seed
		sim['caldb'] = conf.caldb
		sim['irf']   = conf.irf
		sim['ra']   = conf.roi_ra
		sim['dec']  = conf.roi_dec
		sim['rad']  = conf.roi_fov
		# TODO? get time system unit from obsconf.timesys
		sim['tmin'] = "MJD "+str(conf.tstart)
		sim['tmax'] = "MJD "+str(conf.tstop)
		sim['emin'] = conf.emin
		sim['emax'] = conf.emax

		if in_memory:
			logging.info('Generate simulated event list in memory')
			sim.run()
		else:
			logging.info('Generate simulated event list on disk [%s]' % sim['outevents'].value())
			sim.execute()

		logging.debug(sim)
		return sim

	def load_events_from_db(self):
		logging.debug('Load event list from DB')
		#write selected_events_name
		if self.runconf.timeref_timesys == 'tt':
			tstart_tt = self.runconf.tmin
			tstop_tt  = self.runconf.tmax
		elif self.runconf.timeref_timesys == 'mjd':
			tstart_tt = Utility.convert_mjd_to_tt(self.runconf.tmin)
			tstop_tt  = Utility.convert_mjd_to_tt(self.runconf.tmax)
		else:
			logging.error('Unknown time ref system')
			exit(10)

		logging.debug("tstart: %s" % str(tstart_tt))
		logging.debug("tstop:  %s" % str(tstop_tt))
		logging.debug("timeref timesys: %s" % self.runconf.timeref_timesys)

		conf_dictionary = get_path_conf()
		path_base_fits = conf_dictionary['path_base_fits']

		if self.runconf.roi_frame == 'fk5':
			obs_ra  = self.obsconf.roi_ra
			obs_dec = self.obsconf.roi_dec
		else:
			exit(10)

		fov = self.obsconf.roi_fov # unused

		instrument_name = self.obsconf.instrument
		datarepository_dictionary = get_data_repository(instrument_name)
		datarepositoryid = datarepository_dictionary['datarepositoryid']

		observationid = self.obsconf.id
		tref_mjd = self.runconf.timeref

		events_filename = write_fits(tstart_tt, tstop_tt, observationid, datarepositoryid, \
				path_base_fits, tref_mjd, obs_ra, obs_dec, \
				self.runconf.emin, self.runconf.emax, 180, instrument_name)

		logging.debug("fitsname: %s" % events_filename)
		return events_filename

	@staticmethod
	def select_events(obs, conf, output_file=None, in_memory=0):
		select = ctools.ctselect(obs)
		select['ra']   = conf.roi_ra
		select['dec']  = conf.roi_dec
		select['rad']  = conf.roi_ringrad
		select['tmin'] = 'MJD '+ str(conf.tmin)
		select['tmax'] = 'MJD '+ str(conf.tmax)
		select['emin'] = conf.emin
		select['emax'] = conf.emax
		select['outobs'] = output_file

		if in_memory:
			logging.info('Select event list in memory')
			select.run()
		else:
			logging.info('Select event list from disk')
			select.execute()

		logging.debug("ctselect:\n%s" % select)

		logging.debug('=== selection ===')
		logging.debug(select.obs())                   # GObservations
		logging.debug(select.obs()[0])                # GCTAObservation
		logging.debug(select.obs()[0].events())       # GCTAEventList
		logging.debug(select.obs()[0].events().gti()) # GGti
		return select

	# TODO check
	def generate_counts_cube(self, obs, in_memory=0):
		evbin = ctools.ctbin(obs)
		evbin['inobs'] = self.selected_events_file # need? check
		evbin['outcube']  = self.cube_file
		evbin['ebinalg']  = self.runconf.cts_ebinalg
		evbin['emin']     = self.runconf.emin
		evbin['emax']     = self.runconf.emax
		evbin['enumbins'] = self.runconf.cts_enumbins
		evbin['nxpix']    = ceil(self.runconf.roi_ringrad*2 / self.runconf.cts_binsz)
		evbin['nypix']    = ceil(self.runconf.roi_ringrad*2 / self.runconf.cts_binsz)
		evbin['binsz']    = self.runconf.cts_binsz
		evbin['coordsys'] = self.runconf.cts_coordsys
		evbin['usepnt']   = self.runconf.cts_usepnt # Use pointing for map centre
		evbin['proj']     = self.runconf.cts_proj
		evbin['xref']     = self.runconf.roi_ra
		evbin['yref']     = self.runconf.roi_dec

		if in_memory:
			evbin.run()
		else:
			evbin.execute()

			evbin.obs()[0].id(self.cube_file)
			evbin.obs()[0].eventfile(self.cube_file)

			os.system('mkdir -p '+ self.runconf.resdir)
			shutil.copy(self.cube_file, self.runconf.resdir +'/'+ self.runconf.runprefix +'_'+ self.cube_file)

			if self.runconf.CtsMapToPng == 1:
				title = 'OBS '+ str(self.obsconf.id) +' / MJD '+ str(self.runconf.tmin) +' - '+'MJD '+ str(self.runconf.tmax)
				SkyImage.display(self.cube_file, "sky1.png", 2, title)

				os.system('mkdir -p ' + self.runconf.resdir)
				shutil.copy('./sky1.png', self.runconf.resdir +'/'+ self.runconf.runprefix + '_sky1.png')

		# 3GH Extractor code
		# if self.runconf.HypothesisGenerator3GH and self.cube_file:
		# 	self.analysisfilename = CTA3GHextractor_wrapper.extract_source(self.cube_file)
		return evbin.obs().clone()

	def generate_onoff_observation(self, obs, in_memory=0):
		# get RA and DEC from analysisfilename
		model = ET.parse(self.analysisfilename)

		phagen = cscripts.csphagen(obs)
		phagen['ebinalg']   = self.runconf.onoff_ebinalg
		phagen['emin']      = self.runconf.emin
		phagen['emax']      = self.runconf.emax
		phagen['rad']       = float(self.runconf.onoff_radius)
		phagen['ra']        = float(model.find("./source/spatialModel/parameter[@name='RA']").attrib.get('value'))
		phagen['dec']       = float(model.find("./source/spatialModel/parameter[@name='DEC']").attrib.get('value'))
		phagen['enumbins']  = int(self.runconf.onoff_enumbins)
		phagen['stack']     = False
		phagen['bkgmethod'] = self.runconf.onoff_bkgmethod
		phagen['coordsys']  = self.runconf.onoff_coordsys
		phagen['caldb']     = str(self.obsconf.caldb)
		phagen['irf']       = self.obsconf.irf
		phagen['outobs']    = self.onoff_obs_file
		phagen['prefix']    = 'csphagen'
		phagen['logfile']   = 'csphagen.log'

		if in_memory:
			phagen.run()
		else:
			phagen.execute()

		logging.debug('=== onoff ===')
		logging.debug(phagen)
		logging.debug(phagen.obs())                   # GObservations
		logging.debug(phagen.obs()[0])                # GCTAObservation

		return phagen.obs().clone()

	def execute_likelihood(self, obs, binned=0, onoff_analysis=0, in_memory=0):
		logging.debug('before MLE')
		like = ctools.ctlike(obs)
		if onoff_analysis:
			like['inobs'] = self.onoff_obs_file
		else:
			like['inobs'] = self.selected_events_file
		like['inmodel']  = self.analysisfilename
		like['outmodel'] = self.results_file
		like['statistic'] = "DEFAULT"
		like['caldb']     = str(self.obsconf.caldb)
		like['irf']       = self.obsconf.irf
		if binned:
			like['inobs']     = self.cube_file
			like['expcube']   = "NONE"
			like['psfcube']   = "NONE"
			like['edispcube'] = "NONE"
			like['bkgcube']   = "NONE"
			like['statistic'] = "CHI2"

		logging.warn(like)
		like.execute()
		
		logging.warn(like.obs().models())
		logging.debug("after MLE")

		try:
			tree = ET.parse(self.results_file)
			source_tag = tree.find(".//source[@type='PointSource']")
			source_tag.set("runid",str(self.runconf.runid))
			tree.write(self.results_file)

			os.system('mkdir -p '+ self.runconf.resdir)
			shutil.copy(self.results_file, self.runconf.resdir +'/'+ self.runconf.runprefix +'_'+ self.results_file)
		except Exception as e:
			raise e

		if self.runconf.deleterun == "1":
			cmd = 'rm -r '+ self.runconf.rundir
			os.system(cmd)
		return
