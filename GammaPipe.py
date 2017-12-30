import os
import gammalib
import ctools
import obsutils
from Configuration import ObservationConfiguration
from Configuration import RunConfiguration


class GammaPipe:

	def __init__(self):
		return
		
	def init(self, obsfilename, simfilename, analysisfilename, runconffilename, eventfilename):
		self.obsfilename = obsfilename
		self.simfilename = simfilename
		self.analysisfilename = analysisfilename
		self.runconffilename = runconffilename
		self.eventfilename = eventfilename
		
		# Setup observations
		if self.obsfilename:
			self.obs = self.open_observation(self.obsfilename)
		
		# Setup simulation model
		if self.simfilename:
			self.obs.models(gammalib.GModels(self.simfilename))
			
		# Setup run
		if self.runconffilename:
			self.runconf = RunConfiguration(self.runconffilename)
			
		return

	def open_observation(self, obsfilename):

		obs = gammalib.GObservations()
		
		self.obsconf = ObservationConfiguration(obsfilename)

		pntdir = gammalib.GSkyDir()

		#in_pnttype = info_dict['in_pnttype']

		#if in_pnttype == 'celestial' :
			#pntdir.radec_deg(self.obs_ra, self.obs_dec)

		#if in_pnttype == 'equatorial' :
			#pntdir.radec_deg(self.obs_ra, self.obs_dec)

		#if in_pnttype == 'galactic' :
		#	pntdir.radec_deg(self.in_l, self.in_b)

		pntdir.radec_deg(self.obsconf.obs_ra, self.obsconf.obs_dec)

		obs1 = obsutils.set_obs(pntdir, self.obsconf.obs_tstart, self.obsconf.obs_duration, 1.0, \
			self.obsconf.obs_emin, self.obsconf.obs_emax, self.obsconf.obs_fov, \
			self.obsconf.obs_irf, self.obsconf.obs_caldb, self.obsconf.in_obsid)

		obs.append(obs1)

		#print(obs1)
		return obs
		
	#rules
	#1) if simfilename perform simulation based on observation configuration
	#2) if eventfilename read the file. Select events based on run configuration
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
		cubefile_name 	     = 'cube.fits'
		selected_events_name = 'selected_events.fits'
		result_name          = 'results.xml'
		
		if self.simfilename and self.eventfilename:
			print('error')
			exit()

		if self.simfilename:
			if self.runconf.WorkInMemory == 0:
				print('Generate simulated event list on disk')
				# Simulate events on disk
				sim = ctools.ctobssim(self.obs)
				sim['outevents'] = events_name
				sim['debug'] = debug
				sim['seed']    = seed
				sim.execute()
				
			if self.runconf.WorkInMemory == 1:
				print('Generate simulated event list on memory')
				# Simulate events on memory
				sim = ctools.ctobssim(self.obs)
				sim['debug'] = debug
				sim['seed']    = seed
				sim.run()

		if self.eventfilename:
			print('Load event list from disk')
			#Load events from fits file on memory
			sim = ctools.ctobssim(self.obs)
			events = sim.obs()[0].events()
			for event in events:
				print(event)
			events.load(events_name)

		print('event list generated ----------------------')
		print(sim.obs())
		print(sim.obs()[0])

		for run in sim.obs():
			print('run ---')
			# Create container with a single observation
			container = gammalib.GObservations()
			container.append(run)

			#event file in memory or read from fits file on memory
			bin = ctools.ctbin(container)

			#event file on disk
			#bin = ctools.ctbin()
			#bin['inobs']    = events_name


			#make binned map on disk
			bin['outcube']  = cubefile_name

			#common configs
			bin['ebinalg']  = self.runconf.cts_ebinalg
			bin['emin']     = self.runconf.cts_emin
			bin['emax']     = self.runconf.cts_emax
			bin['enumbins'] = self.runconf.cts_enumbins
			bin['nxpix']    = self.runconf.cts_nxpix
			bin['nypix']    = self.runconf.cts_nypix
			bin['binsz']    = self.runconf.cts_binsz
			bin['coordsys'] = self.runconf.cts_coordsys
			bin['usepnt']   = self.runconf.cts_usepnt # Use pointing for map centre
			bin['proj']     = self.runconf.cts_proj

			#make binned map on disk
			bin.execute()
			#make binned map on memory
			#bin.run()

			# Set observation ID if make binned map on disk
			bin.obs()[0].id(cubefile_name)
			bin.obs()[0].eventfile(cubefile_name)

			# Append result to observations
			self.obs.extend(bin.obs())

		#print(obs)
		#print(obs[0])

		# Select events
		# select = ctools.ctselect()
		# 		select['inobs']  = events_name
		# 		select['outobs'] = selected_events_name
		# 		select['ra']     = ra
		# 		select['dec']    = dec
		# 		select['rad']    = rad_select
		# 		select['tmin']   = tstart
		# 		select['tmax']   = tstop
		# 		select['emin']   = emin
		# 		select['emax']   = emax
		# 		select.execute()

		# Perform maximum likelihood fitting
		# 		like = ctools.ctlike()
		# 		like['inobs']    = selected_events_name
		# 		like['inmodel']  = self._model
		# 		like['outmodel'] = result_name
		# 		like['obs_caldb']    = self._obs_caldb
		# 		like['obs_irf']      = self._obs_irf
		# 		like.execute()

		# Return
		return
