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

import os
import shutil
import gammalib
import ctools
import cscripts
import CToolsGammaPipe
from PipeConfiguration import CToolsRunConfiguration
from PipeConfiguration import PostAnalysisCopyFilesConfiguration
from PostAnalysis import *
from ImportResults import *




def execute_import(results_xml):

	ImportResults.import_results(results_xml,1)


def executePostAnalysis(filename):
	# Setup postanalysis
	if filename:
		sessionconf = PostAnalysisCopyFilesConfiguration(filename)

	if sessionconf.postanalysis == "copyfiles":
		copyfiles = PostAnalysisCopyFiles(sessionconf)
		copyfiles.execute()

	merge_results = PostAnalysisMergeResults(sessionconf)
	merge_results.execute()

def pipeline_binned():
	print('Run binned pipeline')
	"""
	Run binned pipeline
	"""
	# Set usage string
	usage = 'ExecuteCTools.py [-observation obsfilename] [-simmodel simmodelfilename] [-anamodel analysismodelfilename] [-confpipe configuration pipe][-seed seed]'

	# Set default options
	options = [{'option': '-observation', 'value': ''}, {'option': '-simmodel', 'value': ''}, {'option': '-anamodel', 'value': ''}, {'option': '-runconf', 'value': ''}, {'option': '-eventfilename', 'value': ''}, {'option': '-seed', 'value': '0'}, {'option': '-postanalysis', 'value': ''}, {'option': '-import', 'value': ''},]

	# Get arguments and options from command line arguments
	args, options = cscripts.ioutils.get_args_options(options, usage)

	# Extract script parameters from options
	obsfilename = options[0]['value']
	simfilename = options[1]['value']
	analysisfilename = options[2]['value']
	runconffilename = options[3]['value']
	eventfilename = options[4]['value']
	in_seed = int(options[5]['value'])
	postanalysis = options[6]['value']
	results_xml = options[7]['value']

	print('obsfilename: ' + obsfilename)
	print('simfilename: ' + simfilename)
	print('analysisfilename: ' + analysisfilename)
	print('runconffilename: ' + runconffilename)
	print('eventfilename: ' + eventfilename)
	print('postanalysis: ' + postanalysis)
	print('results_xml: ' + results_xml)

	if not postanalysis and not results_xml:

		print("not postanalysis not results_xml")
		gp = CToolsGammaPipe.CToolsGammaPipe()

		gp.init(obsfilename, simfilename, analysisfilename, runconffilename, eventfilename)

		# Run analysis pipeline
		gp.run_pipeline(seed=in_seed)

	if results_xml:

		execute_import(results_xml)

	if postanalysis:

		executePostAnalysis(postanalysis)

	# Return
	return


# ======================== #
# Main routine entry point #
# ======================== #
if __name__ == '__main__':

    # Run binned in-memory pipeline
    pipeline_binned()
