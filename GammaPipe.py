import os
import gammalib
import ctools
import obsutils
from read_xml import read_obs_xml


class GammaPipe:

	def __init__(self):
		# Set some standard test data
		self._datadir = os.environ['TEST_DATA']
		self.caldb   = 'prod2'
		self.irf     = 'South_0.5h'
		print('initialised')
		return

	def open_observation(self, obsfilename):

		obs = gammalib.GObservations()
		
		#read XML here
		info_dict = read_obs_xml(obsfilename)

		###usage: in_ra = info_dict['in_ra']

		print info_dict

		#From observation:
		#in_pnttype -> celestial/equatorial or galactic
		#in_ra
		#in_dec
		#in_l
		#in_b
		#in_tstart
		#in_duration
		#in_obsid

		#From target:
		#in_emin
		#in_emax

		#From instrument
		#in_fov
		#in_irf
		#in_caldb

		self.in_ra       =   float(info_dict['in_ra'])
		self.in_dec      =   float(info_dict['in_dec'])
		self.in_fov      =   float(info_dict['in_fov'])
		#rad_select      =    3.0
		self.in_tstart   =   float(info_dict['in_tstart'])
		self.in_duration =   float(info_dict['in_duration'])
		self.in_emin     =   float(info_dict['in_emin'])
		self.in_emax     =   float(info_dict['in_emax'])
		self.caldb 		 =   info_dict['in_caldb'] 
		self.irf	     =   info_dict['in_irf']
		self.in_obsid    =   info_dict['in_obsid']

		pntdir = gammalib.GSkyDir()
		in_pnttype = info_dict['in_pnttype']

		if in_pnttype == 'celestial' :
			pntdir.radec_deg(self.in_ra, self.in_dec)

		if in_pnttype == 'equatorial' :
			pntdir.radec_deg(self.in_ra, self.in_dec)

		#if in_pnttype == 'galactic' :
		#	pntdir.radec_deg(self.in_l, self.in_b)

		obs1 = obsutils.set_obs(pntdir, self.in_tstart, self.in_duration, 1.0, \
			self.in_emin, self.in_emax, self.in_fov, \
			self.irf, self.caldb, self.in_obsid)
			
		obs.append(obs1)

		#print(obs1)
		return obs

	def run_pipeline(self, obs, enumbins=1, nxpix=200, nypix=200, binsz=0.02, debug=False):
		"""
		Test unbinned pipeline with FITS file saving
		"""
		# Set script parameters
		events_name          = 'events.fits'
		cubefile_name 	     = 'cube.fits'
		selected_events_name = 'selected_events.fits'
		result_name          = 'results.xml'

		# Simulate events on disk
		#sim = ctools.ctobssim()
		#sim['outevents'] = events_name
		#sim['debug'] = debug
		#sim.execute()
		
		# Simulate events on memory
		sim = ctools.ctobssim(obs)
		sim['debug'] = debug
		sim.run()
		
		print('simulated ----------------------')
		print(obs)
		print(obs[0])

		for run in sim.obs():
			# Create container with a single observation
			container = gammalib.GObservations()
			container.append(run)
			
			bin = ctools.ctbin(container)
			bin['inobs']    = events_name
			bin['outcube']  = cubefile_name
			bin['ebinalg']  = 'LOG'
			bin['emin']     = self.in_emin
			bin['emax']     = self.in_emax
			bin['enumbins'] = enumbins
			bin['nxpix']    = nxpix
			bin['nypix']    = nypix
			bin['binsz']    = binsz
			bin['coordsys'] = 'CEL'
			bin['usepnt']   = True # Use pointing for map centre
			bin['proj']     = 'CAR'
			bin.execute()

			# Set observation ID
			bin.obs()[0].id(cubefile_name)
			bin.obs()[0].eventfile(cubefile_name)
			# Append result to observations
			obs.extend(bin.obs())

		print(obs)
		print(obs[0])

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
		# 		like['caldb']    = self._caldb
		# 		like['irf']      = self._irf
		# 		like.execute()

		# Return
		return
