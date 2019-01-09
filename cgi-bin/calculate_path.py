#!/usr/bin/env python2
import cgi, cgitb, json, requests, geojson, sys, subprocess, datetime
import check_roads

file_name = "endpoints" + datetime.datetime.now().time().strftime('%X')[:7] + "0.geojson"

form = cgi.FieldStorage() 

start = form.getvalue("Start")
end = form.getvalue("End")
#config = form.getvalue("Config")
#file_name = form.getvalue("File")
config = "./data/pton_config"

split_start = start.split(",")
split_end = end.split(",")

resp_obj = check_roads.check(start=split_start, end=split_end, threshold=0, config_filename=config)

big_dict = dict()
big_dict["type"] = "FeatureCollection"
big_dict["features"] = list()

temp_dict = dict()
temp_dict["type"] = "Feature"
temp_dict["geometry"] = dict()
temp_dict["geometry"]["type"] = "LineString"
temp_dict["geometry"]["coordinates"] = resp_obj["steps"]
temp_dict["properties"] = dict()
temp_dict["properties"]["description"] = "The maximum elev. change is: </p><h3><strong>" + str(resp_obj["gradient"]) + "<p>";
big_dict["features"].append(temp_dict)

subprocess.call("rm data/endpoints*.geojson", shell=True)
with open("data/" + file_name, "w+") as f:
	f.write(json.dumps(big_dict))

print("Content-type:text/html\r\n\r\n")
print("<html>")
print("<head>")
print("<title>Test</title>")
print("</head>")
print("<body>")
print("<h2>Where are you?\n%s</h2>" % (start))
print("</body>")
print("</html>")
