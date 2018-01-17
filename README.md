# ctoolsint

python ExecuteCTools.py  -runconf examples/run_crab.xml -eventfilename events.fits -observation examples/obs_crab.xml

python ExecuteCTools.py -simmodel examples/crab.xml -runconf examples/run_crab.xml -observation examples/obs_crab.xml 

python ExecuteCTools.py -simmodel examples/target_3.xml -runconf examples/run_crab.xml -observation examples/obs_3.xml

Only background

python ExecuteCTools.py -simmodel examples/background.xml -runconf examples/run_cb.xml -observation examples/obs_crab.xml

