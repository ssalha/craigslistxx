#!/usr/bin/env python2.7

import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
from PIL import Image as im
import csv
from sys import exit
import math as m


def mapping(val, stretch, std1, std2 ):
    val = int(val*stretch)
    d1 = np.random.normal(0., std1, val)
    d2 = np.random.normal(0., std2, val)
    return range(val), d1, d2

def distance(x1,y1, x2, y2):
    return (x1-x2)*(x1-x2) + (y1-y2)*(y1-y2)

def pseudoGauss(x, sigma, mu):
    arg = (x - mu)/m.sqrt(2)/sigma
    return m.exp(-arg*arg )


def GaussianPredictor(data, n, minPrice, maxPrice, K):
    """
        GaussianPredictor computes a Gaussian estimation of the probability of observing price
            values at a given (lng, lat, price) from a set of data {(lng_j, lat_j, price_j)_j}.
    """
    Ndata = float(len(data))
    deltaLng = 2.*np.std(np.asarray([u[0] for u in data]))/Ndata
    deltaLat = 2.*np.std(np.asarray([u[1] for u in data]))/Ndata
    uncertainty = 0.5*(maxPrice - minPrice)
    target = minPrice + uncertainty
    predictionMap = []
    for datum in data:
            val = pseudoGauss(datum[2], uncertainty, target)
            pseudoData, d1, d2 = mapping(val, 9., deltaLng, deltaLng )
            for k in pseudoData:
                predictionMap.append((datum[0] + d1[k],\
                                      datum[1] + d2[k],val))
    return predictionMap

