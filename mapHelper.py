#!/usr/bin/env python2

import numpy as np
import matplotlib.pyplot as plt
import mapWrapper as mW
import cPickle as p
from sys import argv, exit
import Image

def filterData(updatedResults, minPrice, maxPrice, tol = 2.):
	"""
		filters the data by price, longitude and latitude

		to filter by longitude & latiude, we use outlier analysis
		first computes mean and standard deviation

		then throws away all data points outside of
		some fraction ('tol'=tolerance) of the mean

		to filter by price, we use user input values
 
	"""
	if minPrice > maxPrice:
		minPrice = 0.
		maxPrice = 10**9
	if minPrice < 0:
		minPrice = 0.
	if maxPrice < 0:
		maxPrice = 10**9

	data = np.asarray( updatedResults )

	# Clean the data (get rid of the outliers)
	meanLngs, meanLats, meanPrices = np.mean(data,axis=0)
	stdLngs, stdLats, stdPrices = np.std(data,axis=0)

	Lats, Lngs, Prices = [], [], []

	for lng, lat, price in data:
		if ((abs(lng - meanLngs) < tol*stdLngs)) \
				and (abs(lat - meanLats) < tol*stdLats)\
				and (price > minPrice) and (price < maxPrice):
			Lngs.append( lng )
			Lats.append( lat )
			Prices.append( price )

	return [Lngs, Lats, Prices]


def center_zoom(Lngs, Lats):
	# Find the bounding box
	minLon, minLat, maxLon, maxLat = min(Lngs), min(Lats), max(Lngs), max(Lats)
	deltaLon, deltaLat = (maxLon - minLon),  (maxLat - minLat)

	centerLon = minLon + .5*deltaLon
	centerLat = minLat + .5*deltaLat

	zoomxfac = 3600.
	zoomyfac = 2925.
	if deltaLon != 0:
		pixXperdeg =  (512.0/deltaLon)
	else:
		pixXperdeg = 1.
	if deltaLat != 0:
		pixYperdeg =  (512.0/deltaLat)
	else:
		pixYperdeg = 1.

	# conversion to zoom
	dx = pixXperdeg/zoomyfac
	dy = pixYperdeg/zoomyfac
	zx = np.floor(12+np.log2(dx))
	zy = np.floor(12+np.log2(dy))
	zoom = min(zx, zy)
	if zoom < 10:
		zoom = 10
	if zoom > 19:
		zoom = 19
	return centerLon, centerLat, zoom

def rescaleSave(mbW, spd, size, foutName):
	# rescale combine and save
	v1, v2 = spd.shape
	norm = np.max(spd)
	spdp = np.round( spd*255./norm )

	spd2 = np.zeros( (v1, v2, 3) ,dtype=np.uint8 )
	spd2[:,:,0] = spdp
	spd_im = Image.fromarray(spd2, 'RGB').resize( (size,size), Image.BICUBIC)

	back_to_numpy = np.array( spd_im, dtype=np.float)
	density_again = np.zeros( (size, size) )
	density_again[:,:] = back_to_numpy[:,:,0]

	density_again /= np.max(density_again)
	mbW.img[:,:,0] = mbW.img[:,:,0]*density_again*255.
	mbW.img[:,:,1] = mbW.img[:,:,1]*density_again*255.
	mbW.img[:,:,2] = mbW.img[:,:,2]*density_again*255.
	im3 = Image.fromarray(np.uint8(mbW.img),mode="RGB")
	im3.save(foutName+".png" )
