from read_xml import read_obs_xml

class RunConfiguration:
	def __init__(self, runconffilename):
	
		info_dict = read_obs_xml(runconffilename)
		
		## Region of Interest
		self.roi_ra = float(info_dict['run']['RegionOfInterest']['ra'])
		self.roi_dec = float(info_dict['run']['RegionOfInterest']['dec'])
		if info_dict['run']['RegionOfInterest']['skypositiontype']:
			self.roi_skypositiontype = int(info_dict['run']['RegionOfInterest']['skypositiontype'])
		else:
			self.roi_skypositiontype = -1
		if info_dict['run']['RegionOfInterest']['ringrad']:
			self.roi_ringrad = float(info_dict['run']['RegionOfInterest']['ringrad'])
		else:
			self.roi_ringrad = -1
		self.roi_AlertContour = info_dict['run']['RegionOfInterest']['AlertContour']
			
		#Time
		self.tmin = float(info_dict['run']['TimeIntervals']['tmin'])
		self.tmax = float(info_dict['run']['TimeIntervals']['tmax'])
		
		#Energy
		self.emin = float(info_dict['run']['Energy']['emin'])
		self.emax = float(info_dict['run']['Energy']['emax'])
		if info_dict['run']['Energy']['energyBinID']:
			self.energyBinID = int(info_dict['run']['Energy']['energyBinID'])
		else:
			self.energyBinID = -1
			
		#pipe configuration
		self.WorkInMemory = int(info_dict['run']['WorkInMemory']['value'])
		self.MakeCtsMap = int(info_dict['run']['MakeCtsMap']['value'])
		#print(info_dict['run']['WorkInMemory']['value'])
		
		#counts map parameters
		self.cts_ebinalg = info_dict['run']['CountsMap']['ebinalg']	
		self.cts_proj = info_dict['run']['CountsMap']['proj']
		self.cts_coordsys = info_dict['run']['CountsMap']['coordsys']
		self.cts_enumbins = int(info_dict['run']['CountsMap']['enumbins'])
		self.cts_nxpix = int(info_dict['run']['CountsMap']['nxpix'])
		self.cts_nypix = int(info_dict['run']['CountsMap']['nypix'])
		self.cts_binsz = float(info_dict['run']['CountsMap']['binsz'])
		self.cts_usepnt = bool(info_dict['run']['CountsMap']['usepnt'])
		
		return
		
class ObservationConfiguration:

	def __init__(self, obsfilename):
	
		# Set some standard test data
		self.obs_caldb   = 'prod2'
		self.obs_irf     = 'South_0.5h'
	
		#read XML
		info_dict = read_obs_xml(obsfilename)
		
		#From observation:
		#in_pnttype -> celestial/equatorial or galactic
		#obs_ra
		#obs_dec
		#in_l
		#in_b
		#obs_tstart
		#obs_duration
		#in_obsid

		#From target:
		#in_emin
		#in_emax

		#From instrument
		#obs_fov
		#in_obs_irf
		#in_obs_caldb

		
		self.obs_ra       =   float(info_dict['observation']['Pointing']['ra'])
		self.obs_dec      =   float(info_dict['observation']['Pointing']['dec'])
		self.obs_fov      =   float(info_dict['observation']['RegionOfInterest']['rad'])
		#rad_select      =    3.0
		self.obs_tstart   =   float(info_dict['observation']['GoodTimeIntervals']['tmin'])
		self.obs_duration =   float(info_dict['observation']['GoodTimeIntervals']['tmax'])-float(info_dict['observation']['GoodTimeIntervals']['tmin'])
		self.obs_emin    =   float(info_dict['observation']['Energy']['emin'])
		self.obs_emax     =   float(info_dict['observation']['Energy']['emax'])
		self.obs_caldb 		 =   info_dict['observation']['Calibration']['database']
		self.obs_irf	     =   info_dict['observation']['Calibration']['response']
		self.in_obsid    =   info_dict['observation']['id']
		
		
		