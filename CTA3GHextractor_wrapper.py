import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
from scipy.stats import norm
import numpy as np
import xml.etree.ElementTree as ET
from astropy.coordinates import SkyCoord
import sys
import CTA3GHextractor
relative_path = '../CTA3GHextractor/'
sys.path.insert(0, relative_path)
from classes import Extractor


def parse_xml(filename):
	tree = ET.parse(filename)
	doc = tree.getroot()

	lf = []
	for source in doc.findall("source"):
		if source.get('type') == 'PointSource':
			curr = [source.get('name')]
			for param in source.findall("spatialModel/parameter"):
				curr.append(float(param.get('value')))
			lf.append(curr)
	return lf


def match_sources(input, other):
	listlist = []
	for found in other:
		current_dist = []
		for i in range(len(input)):
			dist = euclidean_distance(found[1:], input[i][1:])
			current_dist.append(dist)
		min_index = np.argmin(current_dist)
		# mapping found <-> input[min_index]
		listlist.append([found, input[min_index]])
	return listlist


def euclidean_distance(x, y):
	return np.sqrt(np.sum(np.square(np.subtract(x, y))))


def circle_distance(x, y):
	c1 = SkyCoord(x[0], x[1], frame='icrs', unit="deg")
	c2 = SkyCoord(y[0], y[1], frame='icrs', unit="deg")
	sep = c1.separation(c2)
	return sep.deg


def extract_source(cubefile_name):
	xt = Extractor.Extractor(cubefile_name, relative_path+'/')
	return xt.perform_extraction()


def plots(input_res, detection_res, matches):
	# Plot graph

	# # Plot 1: number of spots found
	plt.figure(1)

	plt.title("Number of spots found")
	plt.xlabel('files')
	plt.ylabel("n° detections")
	plt.yticks(range(0, np.max([len(input_res), len(detection_res)]) + 1))

	labels = ['input', 'detected']
	counts = [len(input_res), len(detection_res)]
	plt.bar(labels, counts, color=['r', 'g'])

	# # Plot 2: Detections
	plt.figure(2)

	plt.title("Matches")
	plt.xlabel('RA')
	plt.ylabel("Dec")
	# plt.autoscale = False
	# plt.xlim(80,86)
	# plt.ylim(21, 23)

	for match in matches:
		plt.plot(match[1][1], match[1][2], 'r.')  # input
		plt.plot(match[0][1], match[0][2], 'g^')  # detected

	# # Plot 3: euclidean distance
	plt.figure(3)

	plt.title("Euclidean distance")
	plt.xlabel('RA')
	plt.ylabel("Dec")

	x = np.linspace(-0.2, 0.2, 100)
	x_data, y_data = np.meshgrid(x, x)
	z_data = np.sqrt(np.add(np.square(x_data), np.square(y_data)))
	cs = plt.contourf(x_data, y_data, z_data, levels=np.linspace(0, 1, 50))
	plt.colorbar(cs, format="%.2f")

	for match in matches:
		x_coord = match[0][1] - match[1][1]
		y_coord = match[0][2] - match[1][2]
		plt.plot(x_coord, y_coord, 'r+')
		plt.text(x_coord, y_coord, match[0][0])

	# # Plot 4: binned histogram with fitting gaussian
	plt.figure(4)

	distances = []
	for match in matches:
		dist = circle_distance([match[0][1], match[0][2]], [match[1][1], match[1][2]])
		distances.append(dist)

	hist_bins = np.arange(-0.05, 0.06, 0.01)
	gauss_bins = np.arange(-0.05, 0.06, 0.001)

	(mu, sigma) = norm.fit(distances)
	y = mlab.normpdf(gauss_bins, mu, sigma)

	plt.plot(np.arange(-0.05, 0.06, 0.001), y, 'r--', linewidth=2)
	plt.hist(distances, bins=hist_bins, normed=1, facecolor='green', alpha=0.75)

	plt.xlabel('Bins')
	plt.ylabel('Hist. probabilities')
	plt.title(r'$\mathrm{Fitting\ gaussian:}\ \mu=%.3f,\ \sigma=%.3f$' % (mu, sigma))
	plt.grid(True)

	# # Display
	plt.show()


def print_graphs(inp, ctl, det):
	print('=================================')
	print('Graphs')

	# Parse files
	print("Input_file: {0}".format(inp))
	input_res = parse_xml(inp)
	print(input_res)

	print("Detected_file: {0}".format(det))
	detection_res = parse_xml(det)
	print(detection_res)

	print("CTLike_file: {0}".format(ctl))
	ctlike_res = parse_xml(ctl)
	print(ctlike_res)

	# Find matches
	# # Input vs Detected
	print("Matches: input vs detected")
	matches = match_sources(input_res, detection_res)
	print(matches)

	# # # Input vs CTLike
	print("Matches: input vs ctlike")
	matches_ctl = match_sources(input_res, ctlike_res)
	print(matches_ctl)

	plots(input_res, detection_res, matches)
	plots(input_res, ctlike_res, matches_ctl)
	return

