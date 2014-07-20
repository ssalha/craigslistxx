#!/usr/bin/env python

import cPickle as p
cities = {}

cities['california'] = [["inland empire",'inlandempire'],\
        ["los angeles", 'losangeles'],\
	["modesto","modesto"],\
	["monterey bay", "monterey"],\
	["orange county", "orangecounty"],\
	["redding","redding"],\
	["sacramento", "sacramento"],\
	["san diego", "sandiego"],\
	["san francisco bay area","sfbay"],\
	["santa barbara", "santabarbara"],\
	["stockton","stockton"]]

cities['nevada'] = [("las vegas","lasvegas")]

p.dump(cities, open("cities.p", "wb"))
