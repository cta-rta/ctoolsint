import os
import gammalib
import ctools
import cscripts
import GammaPipe


# ============================= #
# Run binned in-memory pipeline #
# ============================= #
def pipeline_binned():
	print('Run binned pipeline')
	"""
	Run binned pipeline
	"""
	# Set usage string
	usage = 'Pipe1.py [-observation obsfilename] [-simmodel simmodelfilename] [-anamodel analysismodelfilename] [-confpipe configuration pipe][-seed seed]'

	# Set default options
	options = [{'option': '-observation', 'value': ''}, {'option': '-simmodel', '': ''}, {'option': '-anamodel', 'value': 'crab.xml'}, {'option': '-confpipe', 'value': ''}, {'option': '-seed', 'value': '0'}]

	# Get arguments and options from command line arguments
	args, options = cscripts.ioutils.get_args_options(options, usage)

	# Extract script parameters from options
	obsfilename = options[0]['value']
	simfilename = options[1]['value']
	analysisfilename = options[2]['value']
	conffilename = options[3]['value']
	in_seed = int(options[4]['value'])

	print(obsfilename)
	print(simfilename)
	print(analysisfilename)
	print(conffilename)

	gp = GammaPipe.GammaPipe()

	# Setup observations
	obs = gp.open_observation(obsfilename)

	# Setup simulation model
	obs.models(gammalib.GModels(simfilename))

	# Run analysis pipeline
	gp.run_pipeline(obs, enumbins=1, nxpix=200, nypix=200, binsz=0.02, seed=in_seed)

	# Return
	return


# ======================== #
# Main routine entry point #
# ======================== #
if __name__ == '__main__':

    # Run binned in-memory pipeline
    pipeline_binned()
