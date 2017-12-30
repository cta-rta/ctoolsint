# Copyright (c) 2017, AGILE team
# Authors: Nicolo' Parmiggiani <nicolo.parmiggiani@gmail.com>,
#
# Any information contained in this software is property of the AGILE TEAM
# and is strictly private and confidential. All rights reserved.

import xml.etree.ElementTree as ET

def read_obs_xml(filename):

    tree = ET.parse(filename)
    root = tree.getroot()

    info_dic = {}

    print(root.tag)
    info_dic[root.tag] = {}

    for key in root.attrib:
        value =  root.attrib[key]
        info_dic[root.tag][key] = value

    for child in root:
        info_dic[root.tag][child.attrib['name']] = child.attrib

    return info_dic

if __name__ == '__main__':

    # read the XML for the specific observation
    filename = "/tmp/obs_1.xml"
    info_dic = read_obs_xml(filename)
    print(info_dic)
