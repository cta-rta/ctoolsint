
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
from lxml import etree
import glob

class PostAnalysisCopyFiles:
	def __init__(self, sessionconf):
		self.sessionconf = sessionconf
		return

	def execute(self):
		print('copy files')
		if self.sessionconf.WebImage == 1:
			#copy sky1.png
			os.system('mkdir -p ' + self.sessionconf.WebImageDir)
			for entry in os.scandir(self.sessionconf.resdir):
				#print(entry.name)
				if entry.name.endswith('_sky1.png'):
					#print(entry.name)
					shutil.copy(self.sessionconf.resdir + '/' + entry.name, self.sessionconf.WebImageDir + '/sky1.png')
				if entry.name.endswith('_cube.fits'):
					#print(entry.name)
					shutil.copy(self.sessionconf.resdir + '/' + entry.name, self.sessionconf.WebImageDir + '/cube.fits')

		if self.sessionconf.TimeLine == 1:
			os.system('mkdir -p ' + self.sessionconf.TimeLineDir)
			for entry in os.scandir(self.sessionconf.resdir):
				#print(entry.name)
				if  entry.name.endswith('_sky1.png'):
					shutil.copy(self.sessionconf.resdir + '/' + entry.name, self.sessionconf.TimeLineDir)

		return

class PostAnalysisMergeResults:

    def __init__(self, sessionconf):
        self.sessionconf = sessionconf
        return

    def execute(self):

        parser = etree.XMLParser(remove_blank_text=True)
        root = etree.Element("source_library",title="source library")
        #create merget xml

        #for each restults.xml
        count = 0
        for results in glob.glob(self.sessionconf.resdir+'/*_results.xml'):
            print(results)

            result = etree.parse(results,parser)
            #read source object and add to merged xml
            sources = result.findall("//source")

            for source in sources:
                if(source.attrib["type"]=="PointSource"):
                    count = count + 1
                    name = source.attrib["name"]
                    source.attrib["name"] = name+"-"+str(count)
                    
                    root.append(source)

        f = open("results_merged.xml", 'w')
        f.write(etree.tostring(root,encoding="unicode",pretty_print=True))
        f.close()
