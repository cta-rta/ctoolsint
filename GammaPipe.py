import os
import gammalib
import ctools

class ClassPipe:

	def __init__(self):
		# Set some standard test data
		self._datadir = os.environ['TEST_DATA']
		self._model   = self._datadir + '/crab.xml'
		self._caldb   = 'prod2'
		self._irf     = 'South_0.5h'
		print('initialised')
		return
		
	def open_observation(self, filename):
		pntdir = gammalib.GSkyDir()
		#read XML here
		#From observation:
		#in_pnttype -> celestial/equatorial or galactic
		#in_ra
		#in_dec
		#in_l
		#in_b
		#in_tstart
		#in_duration
		
		#in_emin
		#in_emax
		#in_fov
		#in_irf
		#in_caldb
		#in_obsid
		
		if in_pnttype == 'celestial' :
			pntdir.radec_deg(in_ra, in_dec)
			
		if in_pnttype == 'equatorial' :
			pntdir.radec_deg(in_ra, in_dec)
		
		#if in_pnttype == 'galactic' :
		#	pntdir.radec_deg(in_l, in_b)
		
		self.obs = obsutils.set_obs(pntdir, in_tstart, in_duration, 1.0, \
            in_emin, in_emax, in_fov, \
            in_irf, in_caldb, in_obsid):

	def test_unbinned_fits(self):
		"""
		Test unbinned pipeline with FITS file saving
		"""
		# Set script parameters
		events_name          = 'events.fits'
		selected_events_name = 'selected_events.fits'
		result_name          = 'results.xml'
		ra                   =   83.63
		dec                  =   22.01
		rad_sim              =   10.0
		rad_select           =    3.0
		tstart               =    0.0
		tstop                =  300.0
		emin                 =    0.1
		emax                 =  100.0

		# Simulate events
		sim = ctools.ctobssim()
		sim['inmodel']   = self._model
		sim['outevents'] = events_name
		sim['caldb']     = self._caldb
		sim['irf']       = self._irf
		sim['ra']        = ra
		sim['dec']       = dec
		sim['rad']       = rad_sim
		sim['tmin']      = tstart
		sim['tmax']      = tstop
		sim['emin']      = emin
		sim['emax']      = emax
		sim.execute()
		
		

		# Select events
		select = ctools.ctselect()
		select['inobs']  = events_name
		select['outobs'] = selected_events_name
		select['ra']     = ra
		select['dec']    = dec
		select['rad']    = rad_select
		select['tmin']   = tstart
		select['tmax']   = tstop
		select['emin']   = emin
		select['emax']   = emax
		select.execute()

		# Perform maximum likelihood fitting
		like = ctools.ctlike()
		like['inobs']    = selected_events_name
		like['inmodel']  = self._model
		like['outmodel'] = result_name
		like['caldb']    = self._caldb
		like['irf']      = self._irf
		like.execute()

		# Return
		return
