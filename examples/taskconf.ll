xvfb-run -d -s "-screen 0 2000x2000x24" python $PIPELINE/ctoolsint/ExecuteCTools.py -anamodel target.xml -runconf run.xml -observation obs.xml

