import sys

def check(start=None, end=None, threshold=1, config_filename="./data/pton_config"):

	sys.path.append("/usr/local/Cellar/gdal/2.3.2/lib/python2.7/site-packages")

	from osgeo import gdal
	import numpy as np
	import json
	import requests
	import geojson
	import copy

	config_dict = dict()
	with open(config_filename) as f:
		for line in f:
			split_line = line.split(": ")
			config_dict[split_line[0]] = split_line[1][:len(split_line[1]) - 1]

	geo = gdal.Open(config_dict["Alternate"])
	if str(type(geo)) == "<type 'NoneType'>":
		geo = gdal.Open(config_dict["File_Path"])
	elevation = geo.ReadAsArray()

	west = float(config_dict["West_Bounding_Coordinate"])
	east = float(config_dict["East_Bounding_Coordinate"])
	north = float(config_dict["North_Bounding_Coordinate"])
	south = float(config_dict["South_Bounding_Coordinate"])

	TOKEN = "pk.eyJ1Ijoic2FybWFybmVzZW4iLCJhIjoiY2puY2k0NjZvNW9paDNxbjFxZzZldmU0ayJ9.KkaofqOXW8RmbLXhWo6mNA"
	url = "https://api.mapbox.com/directions/v5/mapbox/walking/" + str(float(start[0])) + "," + str(float(start[1])) + ";"
	url +=str(float(end[0])) + "," + str(float(end[1])) + "?&steps=true&access_token=" + TOKEN

	r = requests.get(url)
	geojson_obj = geojson.loads(r.text)

	base = geojson_obj["routes"][0]["legs"][0]["steps"]
	cont = True 
	count = 1
	mgrad_list = list()
	while cont == True:
		intermediate = [[float(start[0]), float(start[1])]]
		for i in base:
			for j in i['intersections']:
				intermediate.append(j['location'])
		intermediate.append([float(end[0]), float(end[1])])

		step_copy = copy.deepcopy(intermediate)

		max_grad = 0
		local_max_grad = 0
		for i in range(0, len(intermediate) - 1):
			ew_change = float(intermediate[i + 1][0]) - float(intermediate[i][0])
			ns_change = float(intermediate[i + 1][1]) - float(intermediate[i][1])

			t_change = ew_change + ns_change

			current = step_copy[i]
			ew_dir = 1
			ns_dir = 1
			if ew_change != 0:
				ew_dir = abs(float(intermediate[i + 1][0]) - float(intermediate[i][0])) / (float(intermediate[i + 1][0]) - float(intermediate[i][0]))
			if ns_change != 0:
				ns_dir = abs(float(intermediate[i + 1][1]) - float(intermediate[i][1])) / (float(intermediate[i + 1][1]) - float(intermediate[i][1]))

			ew_update = ew_dir * (ew_change / t_change)
			ns_update = ns_dir * (ns_change / t_change)

			while (current[0] * ew_dir) < (intermediate[i+1][0] * ew_dir) and (current[1] * ns_dir) < (intermediate[i+1][1] * ns_dir):
				# get the current location in terms of the elevation map
				x = ((current[0] - west) / (east - west)) * len(elevation[0])
				y = ((current[1] - south) / (north - south)) * len(elevation[0])
				x1 = ((current[0] - west) / (east - west)) * len(elevation[0]) + ew_update
				y1 = ((current[1] - south) / (north - south)) * len(elevation[0]) + ns_update
				temp_grad = abs(elevation[int(x1)][int(y1)] - elevation[int(x)][int(y)])
				if temp_grad > local_max_grad:
					local_max_grad = temp_grad
				current[0] += ew_update
				current[1] += ns_update

			if local_max_grad > max_grad:
				max_grad = local_max_grad
			mgrad_list.append(local_max_grad)
			
		if max_grad < threshold or len(geojson_obj["routes"]) == count:
			cont = False
		count += 1

	response = dict()
	response["gradient"] = max_grad 
	response["steps"] = intermediate
	response["step_gradients"] = mgrad_list

	return response