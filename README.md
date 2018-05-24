# ctoolsint

python ExecuteCTools.py  -runconf examples/run_crab.xml -eventfilename events.fits -observation examples/obs_crab.xml -anamodel examples/crab.xml 

python ExecuteCTools.py -simmodel examples/crab.xml -runconf examples/run_crab.xml -observation examples/obs_crab.xml -anamodel examples/crab.xml 

python ExecuteCTools.py -simmodel examples/target-3.xml -runconf examples/run-3-5697.xml -observation examples/obs-3.xml -anamodel examples/target-3.xml

Only background

python ExecuteCTools.py -simmodel examples/background.xml -runconf examples/run_cb.xml -observation examples/obs_crab.xml -anamodel examples/crab.xml

#execute a run 

python ExecuteCTools.py -anamodel examples/target-3.xml -runconf examples/run-3-5697.xml -observation examples/obs-3.xml 

#only simulation
python ExecuteCTools.py -simmodel examples/example2source.xml -runconf examples/run_crab.xml -observation examples/obs_crab.xml

python ExecuteCTools.py -simmodel examples/target-3.xml -observation examples/obs-3.xml 

#Post analysis
python ExecuteCTools.py -postanalysis examples/session.xml
python ExecuteCTools.py -import merged_results.xml

