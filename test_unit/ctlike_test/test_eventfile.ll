#!/bin/bash
#SBATCH --partition=large
#SBATCH --reservation=large_rt
#SBATCH --job-name=cta_pipe_db_RID363
source activate cta_pipe
source /opt/module/cta_rta_pipe_build2 



echo $PYTHONPATH
date +"%T.%N"
python $PIPELINE/ctoolsint/ExecuteCTools.py -anamodel target_south_instr.xml -runconf run.xml -observation obs.xml -eventfilename obs_1_442801819.9999999_442802819.99999976.fits 
date +"%T.%N"
