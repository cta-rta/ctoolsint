import os
import gammalib
import ctools
import obsutils

class GammaPipe:

	def __init__(self):
		# Set some standard test data
		self._datadir = os.environ['TEST_DATA']  
		self._caldb   = 'prod2'
		self._irf     = 'South_0.5h'
		print('initialised')
		return
		
	def open_observation(self, obsfilename):
		
		#read XML here
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
		
		self.in_ra                   =   83.63
		self.in_dec                  =   22.01
		self.in_fov              =   10.0
		#rad_select           =    3.0
		self.in_tstart  =    0.0
		self.in_duration =  300.0
		self.in_emin                 =    0.1
		self.in_emax                 =  100.0
		self.in_obsid = 'OB1000'
		
		pntdir = gammalib.GSkyDir()
		in_pnttype = 'celestial'

		if in_pnttype == 'celestial' :
			pntdir.radec_deg(self.in_ra, self.in_dec)
	
		if in_pnttype == 'equatorial' :
			pntdir.radec_deg(self.in_ra, self.in_dec)

		#if in_pnttype == 'galactic' :
		#	pntdir.radec_deg(self.in_l, self.in_b)

		obs = obsutils.set_obs(pntdir, self.in_tstart, self.in_duration, 1.0, \
			self.in_emin, self.in_emax, self.in_fov, \
			self._irf, self._caldb, self.in_obsid)
	
		return obs

	def run_pipeline(self, obs, simfilename, enumbins=1, nxpix=200, nypix=200, binsz=0.02):
		"""
		Test unbinned pipeline with FITS file saving
		"""
		# Set script parameters
		events_name          = 'events.fits'
		cubefile_name 	     = 'cube.fits'
		selected_events_name = 'selected_events.fits'
		result_name          = 'results.xml'
		

		# Simulate events
		sim = ctools.ctobssim(obs)
		sim['inmodel']   = simfilename
		sim['outevents'] = events_name
		sim['caldb']     = self._caldb
		sim['irf']       = self._irf
		sim.execute()

		#coordsys='GAL', proj='TAN',
		bin = ctools.ctbin(obs)
		bin['inobs']    = events_name
		bin['outcube']  = cubefile_name
		bin['ebinalg']  = 'LOG'
		#bin['emin']     = emin
		#bin['emax']     = emax
		bin['enumbins'] = enumbins
		bin['nxpix']    = nxpix
		bin['nypix']    = nypix
		bin['binsz']    = binsz
		bin['coordsys'] = 'GAL'
		bin['usepnt']   = True # Use pointing for map centre
		bin['proj']     = 'TAN'
		bin.execute()

		# Set observation ID
		bin.obs()[0].id(cubefile_name)
		bin.obs()[0].eventfile(cubefile_name)



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
		



		

