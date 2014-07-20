#!/usr/bin/env python

import cPickle as p
import time
import sys
import mapHelper as mH
import mapWrapper as mW
from sys import exit, argv
sys.path.append("app/crawlers")
import subprocess as sbp
import matplotlib.pyplot as plt
import numpy as np
import dbWrapper as dbW
import logging
import math as m
from PIL import ImageFont

# logging
logging.basicConfig(filename='logstaticPlots.log', \
            format='%(asctime)s %(message)s',\
            datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)

def distance(x1,y1, x2, y2):
	return (x1-x2)*(x1-x2) + (y1-y2)*(y1-y2)

def convert_to_pixels(data, center, zoom, n, orig = False):
    if orig:
        upscale = orig/n
    else:
        upscale = 1.
    sigma_x = 2.**(zoom - 12)*3600. # pixels/degree
    sigma_y = 2.**(zoom - 12)*2925.

    # compute (lng,lat) of upper left corner of image grid
    lng00 = center[0]
    lat00 = center[1]

    xpixels = [(x - lng00)*sigma_x + upscale*n/2. for x in data[0]]
    ypixels = [-(y - lat00)*sigma_y + upscale*n/2. for y in data[1]]

    xpixels = [x/upscale for x in xpixels]
    ypixels = [y/upscale for y in ypixels]

    print max(xpixels), min(xpixels)
    print max(ypixels), min(ypixels)
    pixelated_data = [xpixels, ypixels, data[2]]

    return pixelated_data

def K_NN(data, target, K, n, center, zoom, orig = False):

    #data = convert_to_pixels(data, center, zoom, n, orig=orig) # calling it outside the loop
    Ndata = len(data[0])

    rho = np.zeros( (n,n) )
    
    for x_j in xrange(n):
        for y_j in xrange(n):

            distances = [distance(x_j, y_j, data[0][j], data[1][j]) for j \
                            in xrange(Ndata) ]

            close = np.argsort(distances)[0:K]

            fac1 = np.mean([abs(data[2][u]-target)/500. for u in \
                            close] )
            fac2 = np.mean([distances[u]/20. for u in \
                            close] )
            rho[y_j,x_j] = m.exp( - fac1*fac1  - fac2*fac2 ) + 0.25

    rho[:] /= np.sum(rho)
    return rho


def plotandSave(Data, foutName, city):
	"""Plots histogram for each city. A sublet with 10,000 fee is an outlier"""
	minPrice, maxPrice = 0, 10000 # not sure if we should have the user change this range
	mapData = [[entry[6], entry[5], entry[4]] for entry in Data]
	filteredData = mH.filterData(mapData, minPrice, maxPrice) # filter abnomalous data
	hist, bins = np.histogram(filteredData[2], bins=20, density=True)
	width = 0.7 * (bins[1] - bins[0])
	center = (bins[:-1] + bins[1:]) / 2
	plt.figure()
	plt.bar(center, hist, align='center', width=width)
	plt.xlabel(r'$\mathrm{Price (USD)}$', fontsize = 16)
	plt.ylabel(r'$\mathrm{Frequency}$', fontsize = 16)
	plt.grid(True)
	frame = plt.gca()
	frame.axes.get_yaxis().set_ticks([])
	name = r'$\mathrm{Price\ distribution\ for\ sublets\ in\ %s  } $'%(city )
	plt.title(name, fontsize = 16)
	plt.savefig(foutName+".png")



def predictandSave(knownPostings, foutName, city0, font):
	size = 512 # fixed map size 
	size_s = 64 # used for interpolation
	nn = 20 # nearest neighbors
	nf = 5 #  number of frames
	target = np.zeros(nf)
	deltatarget = 500

	# extract (lng, lat, price) from data.
	# WARNING: THIS IS WRONG - THE DATA IS NOT IN THE DATABASE COORECTLY!
	# LONGITUDE AND LATITUDE ARE BACKWARDS IN THE MYSQL DATABASE!!!!
	mapData = [[entry[6], entry[5], entry[4]] for entry in knownPostings]
	filteredData = mH.filterData(mapData, 0, 1000000) # remove very cheap rents
	centerLon, centerLat, zoom = mH.center_zoom(filteredData[0], filteredData[1])
	center = (centerLon, centerLat)
	filteredData = convert_to_pixels(filteredData, center, zoom, size_s, orig=size)
	target[0] = 500
	for k in xrange(nf):
		if k > 0:
			target[k] = target[k-1] + deltatarget
		outName = "{0}_{1:03d}".format(foutName, k)
		print outName
		# Call to open street map
		mbW = mW.mapboxWrapper(centerLon, centerLat, zoom, size=size)
		#mbW.addMarkers(zip(filteredData[0], filteredData[1]))
		mbW.renderMap()
		#mbW.saveMap(foutName)

		# compute a heat map with 64x64 and 10 neighbors average
		spd = K_NN(filteredData,target[k], nn, size_s,center,zoom,\
									orig=size)
		print target[k]
		text = "$ %03d"%target[k]
		print text
		mH.rescaleSave(mbW, spd, size, outName, text, font)

def main():
	# open the database
	dbObj = dbW.dbWrapper()
	cities_dict = p.load(open("app/cities.p", "rb"))
	font = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeMono.ttf", 33)
	for entry in cities_dict.values():
		for i in range(len(entry)):
				city =  entry[i]; city1 = city[1]; city0 = city[0]
				# Refer to the database, to find the city and postings
				cmd = "select *  from %s group by title;" % (city1)
				try:
					knownPostings = dbObj.query(cmd)
					#foutName = "app/static/images/histo_%s"%city1
					#plotandSave(knownPostings, foutName, city0)
					foutName2 = "app/static/images/predict_%s"%city1
					print foutName2, len(knownPostings[0])
					predictandSave(knownPostings, foutName2, city0, font)
				except Exception as e:
					logging.exception(e)
					print 'Failed. Exiting.'
					raise SystemExit
	dbObj.cursor.close()

if __name__ =='__main__':
	main()


