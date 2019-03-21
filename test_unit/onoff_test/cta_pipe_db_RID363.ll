#!/bin/bash
#SBATCH --partition=large
#SBATCH --reservation=large_rt
#SBATCH --job-name=cta_pipe_db_RID363
source activate cta_pipe
source /opt/module/cta_rta_pipe_build2 



echo $PYTHONPATH
date +"%T.%N"
python $PIPELINE/ctoolsint/ExecuteCTools.py -anamodel target.xml -runconf run.xml -observation obs.xml
date +"%T.%N"
