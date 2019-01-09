import sys

sys.path.append("/usr/local/Cellar/gdal/2.3.2/lib/python2.7/site-packages")

from osgeo import gdal
import numpy as np
import json

big_dict = dict()
big_dict["type"] = "FeatureCollection"
big_dict["features"] = list()

config_dict = dict()
config_filename = sys.argv[1]
with open(config_filename) as f:
	for line in f:
		split_line = line.split(": ")
		config_dict[split_line[0]] = split_line[1][:len(split_line[1]) - 1]

geo = gdal.Open(config_dict["File_Path"])
elevation = geo.ReadAsArray()

west = float(config_dict["West_Bounding_Coordinate"])
east = float(config_dict["East_Bounding_Coordinate"])
north = float(config_dict["North_Bounding_Coordinate"])
south = float(config_dict["South_Bounding_Coordinate"])

start_lon = west
end_lon = east
start_lat = north
end_lat = south
if config_dict["Custom_Bounds"] in ["True", "true"]:
	start_lon = float(config_dict["Custom_West_Bounding_Coordinate"])
	end_lon = float(config_dict["Custom_East_Bounding_Coordinate"])
	start_lat = float(config_dict["Custom_North_Bounding_Coordinate"])
	end_lat = float(config_dict["Custom_South_Bounding_Coordinate"])

i = int(len(elevation) * (start_lon - west) / (east - west))
end_i = int(len(elevation) * (end_lon - west) / (east - west))

j = int(len(elevation[0]) * (start_lat - north) / (south - north))
end_j = int(len(elevation) * (end_lat - north) / (south - north))
start_j = j

once = True
while i < end_i:
	while j < end_j:
		if elevation[i][j] > -10000 and elevation[i][j] < 10000:
			temp_dict = dict()
			temp_dict["type"] = "Feature"
			temp_dict["geometry"] = dict()
			temp_dict["geometry"]["type"] = "Polygon"
			coords = list()
			coords.append([(i * (east - west)/len(elevation)) + west, (j * (south - north)/len(elevation[0])) + north])
			coords.append([(i * (east - west)/len(elevation)) + west, ((j - 10) * (south - north)/len(elevation[0])) + north])
			coords.append([((i - 10) * (east - west)/len(elevation)) + west, ((j - 10) * (south - north)/len(elevation[0])) + north])
			coords.append([((i - 10) * (east - west)/len(elevation)) + west, (j * (south - north)/len(elevation[0])) + north])
			temp_dict["geometry"]["coordinates"] = [[coords[0], coords[1], coords[2], coords[3], coords[0]]]
			temp_dict["properties"] = dict()
			ns_section = sorted(elevation[max(0, i - 10):i].T[j].tolist())
			ew_section = sorted(elevation[j].T[max(0, i - 10):i].T.tolist())
			temp_grad = max(ns_section[len(ns_section) - 1] - ns_section[0], ew_section[len(ew_section) - 1] - ew_section[0])
			temp_dict["properties"]["gradient"] = temp_grad
			big_dict["features"].append(temp_dict)
		j += 10
	j = start_j
	i += 10

json_output = json.dumps(big_dict)
print(json_output)
