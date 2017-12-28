import xml.etree.ElementTree as ET


def read_obs_xml(filename):

    tree = ET.parse(filename)
    root = tree.getroot()

    info_dic = {}

    for observation in root.iter('observation'):
        for key in observation.attrib:
                value =  observation.attrib[key]
                info_dic[key] = value
    for target in root.iter('target'):
        for key in target.attrib:
                value =  target.attrib[key]
                info_dic[key] = value
    for instrument in root.iter('instrument'):
        for key in instrument.attrib:
                value =  instrument.attrib[key]
                info_dic[key] = value


    return info_dic

if __name__ == '__main__':

    # read the XML for the specific observation
    filename = "/tmp/obs_1.xml"
    info_dic = read_obs_xml(filename)
    print info_dic
