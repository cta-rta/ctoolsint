# ==========================================================================
# Utility functions to load configuration objects
#
# Copyright (C) 2018 Andrea Bulgarelli, Nicolò Parmiggiani, Simone Tampieri

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

from GammaPipeCommon.utility import Utility
import xml.etree.ElementTree as ET

def read_xml(filename):
	tree = ET.parse(filename)
	root = tree.getroot()

	info_dic = {}
	info_dic[root.tag] = {}

	for key in root.attrib:
		value = root.attrib[key]
		info_dic[root.tag][key] = value

	for child in root:
		info_dic[root.tag][child.attrib['name']] = child.attrib

	return info_dic

class RunConfiguration:
	def __init__(self, runconffilename):
		self.info_dict = read_xml(runconffilename)
		self.runid     = self.info_dict['run']['id']

		## Region of Interest
		self.roi_unit  = self.info_dict['run']['RegionOfInterest']['unit']
		self.roi_frame = self.info_dict['run']['RegionOfInterest']['frame']
		if self.roi_frame == 'fk5':
			self.roi_ra  = float(self.info_dict['run']['RegionOfInterest']['ra'])
			self.roi_dec = float(self.info_dict['run']['RegionOfInterest']['dec'])
		if self.roi_frame == 'galactic':
			self.roi_l   = float(self.info_dict['run']['RegionOfInterest']['l'])
			self.roi_b   = float(self.info_dict['run']['RegionOfInterest']['b'])
		self.roi_AlertContour = self.info_dict['run']['RegionOfInterest']['AlertContour']

		if self.info_dict['run']['RegionOfInterest']['skypositiontype']:
			self.roi_skypositiontype = int(self.info_dict['run']['RegionOfInterest']['skypositiontype'])
		else:
			self.roi_skypositiontype = -1
		if self.info_dict['run']['RegionOfInterest']['radius']:
			self.roi_ringrad = float(self.info_dict['run']['RegionOfInterest']['radius'])
		else:
			self.roi_ringrad = -1

		#Reference
		self.timeref          = float(self.info_dict['run']['ScienceToolReference']['timestart'])
		self.timeref_timesys  = self.info_dict['run']['ScienceToolReference']['timesys']
		self.timeref_timeunit = self.info_dict['run']['ScienceToolReference']['timeunit']
		self.skyframeref      = self.info_dict['run']['ScienceToolReference']['skyframe']
		self.skyframeunitref  = self.info_dict['run']['ScienceToolReference']['skyframeunit']

		#Space
		if self.skyframeref != self.roi_frame:
			if self.roi_frame == 'fk5':
				self.roi_l, self.roi_b = Utility.convert_fk5_to_gal(self.roi_ra,self.roi_dec)
				self.roi_frame = self.skyframeref
				self.roi_unit  = self.skyframeunitref
			if self.roi_frame == 'galactic':
				self.roi_ra, self.roi_dec = Utility.convert_gal_to_fk5(self.roi_l, self.roi_b)
				self.roi_frame = self.skyframeref
				self.roi_unit  = self.skyframeunitref

		#Time
		self.timesys  = self.info_dict['run']['TimeIntervals']['timesys']
		self.timeunit = self.info_dict['run']['TimeIntervals']['timeunit']
		tmin = float(self.info_dict['run']['TimeIntervals']['tmin'])
		tmax = float(self.info_dict['run']['TimeIntervals']['tmax'])

		if self.timeref_timesys != self.timesys:
			if self.timesys == 'mjd':
				tmin = Utility.convert_mjd_to_tt(tmin)
				tmax = Utility.convert_mjd_to_tt(tmax)
				self.timesys  = self.timeref_timesys
				self.timeunit = self.timeref_timeunit
			if self.timesys == 'tt':
				tmin = Utility.convert_tt_to_mjd(tmin)
				tmax = Utility.convert_tt_to_mjd(tmax)
				self.timesys  = self.timeref_timesys
				self.timeunit = self.timeref_timeunit

		self.tmin = tmin
		self.tmax = tmax

		#timeref, timesys, timeunit is common

		#Energy
		self.emin = float(self.info_dict['run']['Energy']['emin'])
		self.emax = float(self.info_dict['run']['Energy']['emax'])
		if self.info_dict['run']['Energy']['energyBinID']:
			self.energyBinID = int(self.info_dict['run']['Energy']['energyBinID'])
		else:
			self.energyBinID = -1

		#Dir configuration
		self.rundir    = self.info_dict['run']['DirectoryList']['run']
		self.resdir    = self.info_dict['run']['DirectoryList']['results']
		self.runprefix = self.info_dict['run']['DirectoryList']['runprefix']
		return

class ObservationConfiguration:
	def __init__(self, obsfilename, timesys, timeunit, skyframeref, skyframeunitref):
		info_dict = read_xml(obsfilename)

		#Pointing
		self.point_frame = info_dict['observation']['Pointing']['frame']
		if self.point_frame == 'fk5':
			self.point_ra  = float(info_dict['observation']['Pointing']['ra'])
			self.point_dec = float(info_dict['observation']['Pointing']['dec'])
		if self.point_frame == 'galactic':
			self.point_l   = float(info_dict['observation']['Pointing']['l'])
			self.point_b   = float(info_dict['observation']['Pointing']['b'])
		self.point_unit = info_dict['observation']['Pointing']['unit']

		if skyframeref != self.point_frame:
			if self.point_frame == 'fk5':
				self.point_l, self.point_b = Utility.convert_fk5_to_gal(self.point_ra, self.point_dec)
				self.point_frame = skyframeref
				self.point_unit  = skyframeunitref
			if self.point_frame == 'galactic':
				self.point_ra, self.point_dec = Utility.convert_gal_to_fk5(self.point_l, self.point_b)
				self.point_frame = skyframeref
				self.point_unit  = skyframeunitref

		#Region of Interest
		self.roi_frame = info_dict['observation']['RegionOfInterest']['frame']
		if self.roi_frame == 'fk5':
			self.roi_ra  = float(info_dict['observation']['RegionOfInterest']['ra'])
			self.roi_dec = float(info_dict['observation']['RegionOfInterest']['dec'])
		if self.roi_frame == 'galactic':
			self.roi_l   = float(info_dict['observation']['RegionOfInterest']['l'])
			self.roi_b   = float(info_dict['observation']['RegionOfInterest']['b'])
		self.roi_unit = info_dict['observation']['RegionOfInterest']['unit']
		if skyframeref != self.roi_frame:
			if self.roi_frame == 'fk5':
				self.roi_l, self.roi_b = Utility.convert_fk5_to_gal(self.roi_ra, self.roi_dec)
				self.roi_frame  = skyframeref
				self.roi_unit   = skyframeunitref
			if self.roi_frame == 'galactic':
				self.roi_ra, self.roi_dec = Utility.convert_gal_to_fk5(self.roi_l, self.roi_b)
				self.roi_frame  = skyframeref
				self.roi_unit   = skyframeunitref

		self.roi_fov = float(info_dict['observation']['RegionOfInterest']['rad'])

		self.timesys  = info_dict['observation']['GoodTimeIntervals']['timesys']
		self.timeunit = info_dict['observation']['GoodTimeIntervals']['timeunit']
		tmin = float(info_dict['observation']['GoodTimeIntervals']['tstartreal'])
		tmax = info_dict['observation']['GoodTimeIntervals']['tendreal']
		if(tmax != "None"):
			tmax = float(tmax)

		self.tstart = tmin
		self.tstop  = tmax

		if timesys != self.timesys:
			if self.timesys == 'mjd':
				self.tstart = Utility.convert_mjd_to_tt(tmin)
				if(tmax != "None"):
					self.tstop = Utility.convert_mjd_to_tt(tmax)
			if self.timesys == 'tt':
				self.tstart = Utility.convert_tt_to_mjd(tmin)
				if(tmax != "None"):
					self.tstop = Utility.convert_tt_to_mjd(tmax)

		self.timesys  = timesys
		self.timeunit = timeunit
		self.duration = self.tstop - self.tstart

		if self.timesys == 'mjd':
			self.duration = float(self.duration) * 86400.0

# 		if self.obs_timesys == 'tt':
# 			tmin = float(info_dict['observation']['GoodTimeIntervals']['tmin'])
# 			tmax = float(info_dict['observation']['GoodTimeIntervals']['tmax'])
# 			self.obs_duration =   tmax - tmin
# 			self.obs_tstart = tmin
# 			self.obs_tstop = tmax;

		#la parte qui sotto va mossa nel run, perché serve l'mjdref
		#self.obs_tstart   =   (tmin - 55197.000766018518519) * 86400
		self.emin  = float(info_dict['observation']['Energy']['emin'])
		self.emax  = float(info_dict['observation']['Energy']['emax'])
		self.caldb = info_dict['observation']['Calibration']['database']
		self.irf   = info_dict['observation']['Calibration']['response']
		self.id    = info_dict['observation']['id']
		self.name  = info_dict['observation']['name']
		self.instrument = info_dict['observation']['instrument']
		self.deadtime = float(info_dict['observation']['Deadtime']['deadc'])
		return

	def __str__(self):
		return str(self.__class__) +": "+ str(self.__dict__)

class CToolsRunConfiguration(RunConfiguration):
	def __init__(self, filename):
		RunConfiguration.__init__(self,filename)

		#pipe configuration
		self.WorkInMemory = int(self.info_dict['run']['WorkInMemory']['value'])

		self.MakeCtsMap  = int(self.info_dict['run']['MakeCtsMap']['value'])
		self.CtsMapToPng = int(self.info_dict['run']['CtsMapToPng']['value'])

		self.HypothesisGenerator3GH = int(self.info_dict['run']['HypothesisGenerator3GH']['value'])

		#counts map parameters
		self.cts_ebinalg = self.info_dict['run']['CountsMap']['ebinalg']
		self.cts_proj    = self.info_dict['run']['CountsMap']['proj']
		self.cts_coordsys = self.info_dict['run']['CountsMap']['coordsys']
		self.cts_enumbins = int(self.info_dict['run']['CountsMap']['enumbins'])
		#self.cts_nxpix = int(self.info_dict['run']['CountsMap']['nxpix'])
		#self.cts_nypix = int(self.info_dict['run']['CountsMap']['nypix'])
		self.cts_binsz = float(self.info_dict['run']['CountsMap']['binsz'])

		self.binned = self.info_dict['run']['Binned']['value']
		self.deleterun = self.info_dict['run']['DeleteRun']['value']

		#Onoff
		self.onoff_analysis = int(self.info_dict['run'].get('ScienceToolReference', {}).get('onoff', '0'))
		if self.onoff_analysis:
			onoff_params = self.info_dict['run'].get('OnOff', {})

			if not onoff_params:
				print("Error: need a OnOff param tag in run config")
				exit(1)

			for param in ['ebinalg', 'enumbins', 'bkgmethod', 'coordsys', 'radius']:
				if param in onoff_params:
					setattr(self, 'onoff_'+param, onoff_params[param])
				else:
					print("Error: '%s' parameter is not in run config OnOff tag." % param)
					exit(1)

		point_to_center_of_observation = self.info_dict['run']['CountsMap']['usepnt']
		if(point_to_center_of_observation == "yes"):
			self.cts_usepnt = True
		else:
			self.cts_usepnt = False

	def __str__(self):
		return str(self.__class__) +": "+ str(self.__dict__)

class PostAnalysisConfiguration:
	def __init__(self, sessionconffilename):
		self.info_dict    = read_xml(sessionconffilename)
		self.sessionid    = self.info_dict['session']['id']
		self.postanalysis = self.info_dict['session']['postanalysis']['value']

class PostAnalysisCopyFilesConfiguration(PostAnalysisConfiguration):
	def __init__(self, sessionconffilename):
		PostAnalysisConfiguration.__init__(self, sessionconffilename)
		self.resdir      = self.info_dict['session']['DirectoryList']['results']
		self.WebImage    = int(self.info_dict['session']['WebImage']['value'])
		self.WebImageDir = self.info_dict['session']['WebImage']['dir']
		self.TimeLine    = int(self.info_dict['session']['TimeLine']['value'])
		self.TimeLineDir = self.info_dict['session']['TimeLine']['dir']
