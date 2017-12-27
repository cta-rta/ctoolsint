import os
import gammalib
import ctools
import cscripts
import GammaPipe


# ============================= #
# Run binned in-memory pipeline #
# ============================= #
def pipeline_binned_mem():
    """
    Run binned pipeline
    """
    # Set usage string
    usage = 'pipeline_binned_mem.py [-d datadir]'

    # Set default options
    options = [{'option': '-o', 'obs': 'observation'}, {'option': '-s', 'sim': 'simmodel'}, {'option': '-a', 'an': 'analysismodel'}, {'option': '-c', 'conf': 'confpipe'},]
    

    # Get arguments and options from command line arguments
    args, options = cscripts.ioutils.get_args_options(options, usage)

    # Extract script parameters from options
    obsfilename = options[0]['obs']
    simfilename = options[0]['sim']
    analysisfilename = options[0]['an']
    conffilename = options[0]['conf']
    
    gp = GammaPipe()
    
    obs = gp.open_observation(obsfilename)

    # Setup observations

    # Setup model
    obs.models(gammalib.GModels(simfilename))

    # Run analysis pipeline
    run_pipeline(obs, enumbins=1, nxpix=200, nypix=200, binsz=0.02)

    # Return
    return


# ======================== #
# Main routine entry point #
# ======================== #
if __name__ == '__main__':

    # Run binned in-memory pipeline
    pipeline_binned_mem()
