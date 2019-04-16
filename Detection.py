import ctools
import gammalib
import logging
import obsutils
from conf import * # get_path_conf, get_data_repository
from CTAGammaPipeCommon.create_fits import write_fits # DB connection
from GammaPipeCommon.Configuration import ObservationConfiguration
from GammaPipeCommon.utility import Utility

# FIXME doubts
# * simulation from observation (obs.xml) or not?
# * load events from db: we don't use fov. is it right?
#                        workInMemory == 2 ? what expected from events.load() ?
class Detection:
	DEFAULT_EVENTS_FILE   = 'events.fits'
	DEFAULT_SELECTED_FILE = 'selected_events.fits'
	DEFAULT_CUBECNT_FILE  = 'cube.fits'
	DEFAULT_RESULTS_FILE  = 'results.xml'

	def __init__(self, args):
		self.obsfilename      = args['obsfilename']
		self.simfilename      = args['simfilename']
		self.analysisfilename = args['analysisfilename']
		self.eventfilename    = args['eventfilename']
		self.runconf          = args['runconf']

		self.events_file = self.eventfilename or self.DEFAULT_EVENTS_FILE
		self.selected_events_file = self.DEFAULT_SELECTED_FILE
		self.cube_file = self.DEFAULT_CUBECNT_FILE
		self.results_file = self.DEFAULT_RESULTS_FILE

		self.obs = None
		self.obsconf = None

		if self.obsfilename:
			self.obsconf = ObservationConfiguration(self.obsfilename, self.runconf.timesys, self.runconf.timeunit, self.runconf.skyframeref, self.runconf.skyframeunitref)
			self.obs = self.create_observation()

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

	def create_observation(self):
		# check against self.obsconf + self.runconf
		pntdir = gammalib.GSkyDir()
		if self.obsconf.point_frame == 'fk5':
			pntdir.radec_deg(self.obsconf.point_ra, self.obsconf.point_dec)
	
		tstart = self.obsconf.tstart - self.runconf.timeref
		logging.info('tstart diff: %s (days)' % str(tstart))
		if self.runconf.timeref_timesys == 'mjd':
			tstart = tstart * 86400.0
		logging.info('TSTART: %s (sec)' % str(tstart))

		cta_obs = obsutils.set_obs(pntdir, tstart, self.obsconf.duration, 1.0, \
			self.obsconf.emin, self.obsconf.emax, self.obsconf.roi_fov, \
			self.obsconf.irf, self.obsconf.caldb, self.obsconf.id)

		logging.info('CTA Observation events:\n%s' % cta_obs.events().gti())

		obs = gammalib.GObservations()
		obs.append(cta_obs)
		return obs

	def run_pipeline(self, debug=False, seed=0):
		simulation, events_file = self.get_events_simulation(debug, seed)

		selection = self.select_events(simulation, events_file)

		# FIXME why we use different GObservations object if we work in memory or not?
		if self.runconf.WorkInMemory == 0:
			gobs = self.obs
		elif self.runconf.WorkInMemory == 1:
			gobs = selection.obs()

		# FIXME useless loop (?)
		# the gobs has only one GCTAObservation
		# for gctao in gobs:
		# 	container = gammalib.GObservations()
		# 	container.append(gctao)
		if self.runconf.MakeCtsMap == 1:
			self.generate_counts_cube(gobs)

		if self.analysisfilename:
			self.execute_likelihood(selection)

		return

	def get_events_simulation(self, debug, seed):
		events_file = None
		simulation  = None

		if self.simfilename and self.eventfilename:
			logging.error('cannot works with simfilename && eventfilename')
			exit(10)

		if self.simfilename:
			simulation, events_file = self.create_events_simulation(debug, seed)

		if not self.simfilename and not self.eventfilename:
			events_file = self.load_events_from_db()

		return simulation, events_file

	# FIXME if work on disk => get inmodel and wrote on events_file
	#       if work in memory => start from observation and doesn't write
	def create_events_simulation(self, debug, seed):
		"""
		Return a ctobssim GApplication using the simulation model filename as inmodel.
		"""
		events_file = None

		self.obs.models(gammalib.GModels(self.simfilename))

		sim = ctools.ctobssim(self.obs)
		sim['debug'] = debug
		sim['seed']  = seed

		if self.runconf.WorkInMemory == 0:
			events_file = self.events_file
			logging.info('Generate simulated event list on disk [%s]' % events_file)
			sim['outevents'] = events_file
			# sim['caldb'] = 'prod2'
			# sim['irf']   = 'South_0.5h'
			# sim['ra']   = self.obsconf.roi_ra
			# sim['dec']  = self.obsconf.roi_dec
			# sim['rad']  = self.obsconf.roi_fov
			# sim['tmin'] = "MJD "+str(self.obsconf.tstart)
			# sim['tmax'] = "MJD "+str(self.obsconf.tstop)
			# sim['emin'] = self.obsconf.emin
			# sim['emax'] = self.obsconf.emax
			sim.execute()
		elif self.runconf.WorkInMemory == 1:
			logging.info('Generate simulated event list in memory')
			sim.run()

		return sim, events_file

	def load_events_from_db(self):
		logging.debug('Load event list from DB')
		#write selected_events_name
		if self.runconf.timeref_timesys == 'tt':
			tstart_tt = self.runconf.tmin
			tstop_tt  = self.runconf.tmax
		if self.runconf.timeref_timesys == 'mjd':
			tstart_tt = Utility.convert_mjd_to_tt(self.runconf.tmin)
			tstop_tt  = Utility.convert_mjd_to_tt(self.runconf.tmax)

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

		logging.info("before write fits")
		events_filename = write_fits(tstart_tt, tstop_tt, observationid, datarepositoryid, \
				path_base_fits, tref_mjd, obs_ra, obs_dec, \
				self.runconf.emin, self.runconf.emax, 180, instrument_name)
		logging.info("after write fits")

		logging.debug("fitsname: %s" % events_filename)
		# FIXME what is the use of following lines?
		#       we load selected events in events, but we 
		# if self.runconf.WorkInMemory == 2:
		# 	logging.info('Load event list from disk')
		# 	sim = ctools.ctobssim(self.obs)
		# 	events = sim.obs()[0].events()
		# 	for event in events:
		# 		logging.debug(event)
		# 	events.load(self.selected_events_file)

		return events_filename

	def select_events(self, sim, events_file):
		select = ctools.ctselect(sim.obs())
		select['ra']   = self.runconf.roi_ra
		select['dec']  = self.runconf.roi_dec
		select['rad']  = self.runconf.roi_ringrad
		select['tmin'] = 'MJD ' + str(self.runconf.tmin)
		select['tmax'] = 'MJD ' + str(self.runconf.tmax)
		select['emin'] = self.runconf.emin
		select['emax'] = self.runconf.emax

		if self.runconf.WorkInMemory == 0:
			logging.info('Select event list from disk')
			select['inobs']  = events_file
			select['outobs'] = self.selected_events_file
			select.execute()

		if self.runconf.WorkInMemory == 1:
			logging.info('Select event list in memory')
			select.run()

		logging.info('After select events')
		logging.debug("ctselect:\n%s" % select)
		return select

	def generate_counts_cube(self, container):
		if self.runconf.WorkInMemory == 0:
			bin = ctools.ctbin()
			bin['inobs'] = self.selected_events_file
		elif self.runconf.WorkInMemory == 1:
			bin = ctools.ctbin(container)

		bin['outcube']  = self.cube_file
		bin['ebinalg']  = self.runconf.cts_ebinalg
		bin['emin']     = self.runconf.emin
		bin['emax']     = self.runconf.emax
		bin['enumbins'] = self.runconf.cts_enumbins
		bin['nxpix']    = ceil(self.runconf.roi_ringrad*2 / self.runconf.cts_binsz)
		bin['nypix']    = ceil(self.runconf.roi_ringrad*2 / self.runconf.cts_binsz)
		bin['binsz']    = self.runconf.cts_binsz
		bin['coordsys'] = self.runconf.cts_coordsys
		bin['usepnt']   = self.runconf.cts_usepnt # Use pointing for map centre
		bin['proj']     = self.runconf.cts_proj
		bin['xref']     = self.runconf.roi_ra
		bin['yref']     = self.runconf.roi_dec

		if self.runconf.WorkInMemory == 0:
			bin.execute()

			# FIXME unused
			# bin.obs()[0].id(self.cube_file) # FIXME is it right?
			# bin.obs()[0].eventfile(self.cube_file)

			os.system('mkdir -p '+ self.runconf.resdir)
			shutil.copy(self.cube_file, self.runconf.resdir +'/'+ self.runconf.runprefix +'_'+ self.cube_file)

			if self.runconf.CtsMapToPng == 1:
				title = 'OBS '+ str(self.obsconf.id) +' / MJD '+ str(self.runconf.tmin) +' - '+'MJD '+ str(self.runconf.tmax)
				SkyImage.display(cubefile_name, "sky1.png", 2, title)

				os.system('mkdir -p ' + self.runconf.resdir)
				shutil.copy('./sky1.png', self.runconf.resdir +'/'+ self.runconf.runprefix + '_sky1.png')
		elif self.runconf.WorkInMemory == 1:
			bin.run()

		# 3GH Extractor code
		# if self.runconf.HypothesisGenerator3GH and self.cube_file:
		# 	self.analysisfilename = CTA3GHextractor_wrapper.extract_source(self.cube_file)

		return

	def execute_likelihood(self, select):
		logging.debug('before MLE')
		if self.runconf.WorkInMemory == 0:
			like = ctools.ctlike()
			if(self.runconf.binned == "0"):
				like['inobs']     = self.selected_events_file
				like['statistic'] = "DEFAULT"
			elif(self.runconf.binned == "1"):
				like['inobs']     = self.cube_file
				like['expcube']   = "NONE"
				like['psfcube']   = "NONE"
				like['edispcube'] = "NONE"
				like['bkgcube']   = "NONE"
				like['statistic'] = "CHI2"
		elif self.runconf.WorkInMemory == 1:
			like = ctools.ctlike(select.obs())

		like['inmodel']  = self.analysisfilename
		like['outmodel'] = self.results_file
		like['caldb']    = str(self.obsconf.caldb)
		like['irf']      = self.obsconf.irf

		like.execute()
		logging.warn(like)
		# logL = like.opt().value()
		logging.warn(like.obs().models())
		logging.debug("after MLE")

		# insert logL into results.xml
		tree = etree.parse(self.results_file)
		contentnav = tree.find(".//source[@type='PointSource']")
		# contentdiv = contentnav.getparent()
		# contentnav.set("ts",str(logL))
		contentnav.set("runid",str(self.runconf.runid))
		# print(etree.tostring(tree,encoding="unicode",pretty_print=True))
		# TODO check why here we write
		f = open(self.results_file, 'w')
		f.write(etree.tostring(tree, encoding="unicode", pretty_print=True))
		f.close()

		os.system('mkdir -p '+ self.runconf.resdir)
		shutil.copy(self.results_file, self.runconf.resdir +'/'+ self.runconf.runprefix +'_'+ self.results_file)

		if self.runconf.deleterun == "1":
			cmd = 'rm -r '+ self.runconf.rundir
			os.system(cmd)
		return
