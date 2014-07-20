#!/usr/bin/env python2.7

'''
This functions is the map box, using Open Street Map wrapper.

1) It opens the file for longitude, latitude , price in mapUpdated.p

2) It filters the file in case of outliers. 

3) It generates a bounding box map with the correct 

4) To do, add the heat map. 

'''


import numpy as np
import requests
import sys
import matplotlib.pyplot as plt
import matplotlib.image as mpImg
import io
import cPickle as p

class mapboxWrapper:

	def __init__(self, centerLon, centerLat, zoom, size = 512):
		"""
			centerLon: center of image to be rendered (longitude)
			centerLat: center of image to be rendered (latitude)
		"""

		#----------------------------------------------------------------------
		# some constants
		#----------------------------------------------------------------------

		# base url is the url that we need for all requests.
		self.base_url = "http://api.tiles.mapbox.com/v4/"

		# this is my account and map ID for rendering
		self.map_id = "************"

		# account token for authorizing requests
		self.token = "?access_token=***************************"

		# we generally want PNG format images so I'm just fixing this in the initialization.
		self.imFormat = ".png"

		# unitConversion allows us to assign (lon,lat) coordinates to each pixel
		# unitConversion[zoom] = (# columns per degree longitude, # rows per degree latitude)

		self.unitConversion = {12: (360., 292.),
								11: (180., 146. ),
								10: (90., 73. )}
		self.url = ''
		self.img = ''

		#----------------------------------------------------------------------
		# Set Map Details
		#----------------------------------------------------------------------
		self.centerLon = centerLon
		self.centerLat = centerLat
		self.size = size
		self.zoom = "," + str(zoom) + "/"

		self.coords_string = "{0},{1}".format(centerLon, centerLat)

		self.size_string = "{0}x{0}".format(size)
		self.markers = ''

	def addMarkers(self, LngLatList):
		markers = ''
		for lng,lat in LngLatList:
			markers += "pin-s({0},{1}),".format(lng,lat)
		self.markers = markers[:-1] + '/'


	def renderMap(self):

		self.url += self.base_url + self.map_id
		if len(self.markers) > 5:
			self.url += self.markers
		self.url += self.coords_string
		self.url += self.zoom + self.size_string + self.imFormat + self.token

		response = requests.get(self.url) 
		status = response.status_code
		if status == 200:
			# it is convenient if we convert the image string into a stream
			try:
				self.imageResponse = response.content
				stream = io.BytesIO(self.imageResponse )

				# it is even more convenient if we convert the stream
				# into a numpy array (plt.imread does this)
				self.img = plt.imread(stream)
			except Exception as e:
				print e
				print self.url
				raise Exception

		else:
			print response.text
			print self.url
			raise RuntimeError('bad url')

	def showMap(self, title):

		if len(self.img) > 0:
			plt.imshow(self.img, interpolation='nearest')
			plt.title(title, fontsize = 22)
			plt.show()
		else:
			raise RuntimeError("No Image.")

	def saveMap(self, outName):
		if '.png' not in outName:
			outName += '.png'
		with open(outName, "w") as fout:
			fout.write(self.imageResponse)

