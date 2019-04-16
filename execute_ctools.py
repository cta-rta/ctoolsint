#!/usr/bin/env python

# we need Utility in GammaPipeCommon/Configuration.py
from GammaPipeCommon.utility import Utility

import cscripts
import logging
from PipeConfiguration import CToolsRunConfiguration
from PipeConfiguration import PostAnalysisCopyFilesConfiguration
from PostAnalysis import *
import Detection

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s:%(levelname)s:%(message)s',)

def run():
	"""
	Run the pipeline
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
	# logging.debug('params:\n%s' % params)
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
	return

def executeDetection(params):
	"""
	setup and execute the detection
	"""
	logging.debug('runconf file: %s' % params['runconffilename'])
	params['runconf'] = CToolsRunConfiguration(params['runconffilename'])
	gp = Detection.Detection(params) # obsfilename, simfilename, analysisfilename, runconf, eventfilename)
	gp.run_pipeline(seed=params['in_seed'])
	return

if __name__ == '__main__':
	run()
