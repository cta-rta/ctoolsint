# ==========================================================================
# Helper class for ctools integration into the Science Alert Generation system
#
# Copyright (C) 2018 Andrea Bulgarelli, Nicolo' Parmiggiani
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
import cscripts
import logging
import Detection
from PipeConfiguration import CToolsRunConfiguration
from PipeConfiguration import PostAnalysisCopyFilesConfiguration
from PostAnalysis import *

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s:%(levelname)s:%(message)s',)

def run_pipeline():
	"""
	Run pipeline
	"""
	params = init_params()
	logging.info("before run pipe")
	if params['postanalysis']:
		executePostAnalysis(params['postanalysis'])
	else:
		executeDetection(params)
	logging.info("after run pipe")
	return

def init_params():
	usage = 'ExecuteCTools.py [-observation obsfilename] [-simmodel simmodelfilename] [-anamodel analysismodelfilename] [-confpipe configuration pipe][-seed seed]'
	options = [
			{'option': '-observation', 'value': ''},
			{'option': '-simmodel',      'value': ''},
			{'option': '-anamodel',      'value': ''},
			{'option': '-runconf',       'value': ''},
			{'option': '-eventfilename', 'value': ''},
			{'option': '-seed',          'value': '0'},
			{'option': '-postanalysis',  'value': ''}
	]
	# Get arguments and options from command line arguments
	args, options = cscripts.ioutils.get_args_options(options, usage)
	# logging.debug('args: %s' % args)
	# logging.debug('options: %s' % options)
	# Extract script parameters from options
	params = {
			'obsfilename':      options[0]['value'],
			'simfilename':      options[1]['value'],
			'analysisfilename': options[2]['value'],
			'runconffilename':  options[3]['value'],
			'eventfilename':    options[4]['value'],
			'in_seed':          int(options[5]['value']),
			'postanalysis':     options[6]['value']
	}
	logging.debug('params: %s' % params)
	return params

def executePostAnalysis(filename):
	"""
	setup and execute post analysis
	"""
	logging.debug('execute post-analysis on file "%s"', filename)
	try:
		sessionconf = PostAnalysisCopyFilesConfiguration(filename)
	except Exception as e:
		raise e

	if sessionconf.postanalysis == "copyfiles":
		copyfiles = PostAnalysisCopyFiles(sessionconf)
		copyfiles.execute()
	merge_results = PostAnalysisMergeResults(sessionconf)
	merge_results.execute()

def executeDetection(params):
	"""
	setup and execute detection
	"""
	logging.debug('runconf file: %s' % params['runconffilename'])
	params['runconf'] = CToolsRunConfiguration(params['runconffilename'])
	logging.debug('params[runconf]: %s' % params['runconf'])
	exit(0)
	gp = Detection.Detection(params) # obsfilename, simfilename, analysisfilename, runconf, eventfilename)
	gp.run_pipeline(seed=params['in_seed'])
	# if runconf.onoff_analysis == 1:
	# 	print("starting on/off analysis")
	# 	gp = DetectionOnOff.DetectionOnOff()
	# else:
	# 	print("starting detection and maps")
	# 	gp = DetectionAndMaps.DetectionAndMaps()
	# gp.init(obsfilename, simfilename, analysisfilename, runconf, eventfilename)
	# gp.run_pipeline(seed=in_seed)
	return

# ======================== #
# Main routine entry point #
# ======================== #
if __name__ == '__main__':
    run_pipeline()
