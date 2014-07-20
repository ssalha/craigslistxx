from flask import Flask, render_template, request, jsonify, redirect, url_for
from app import app, host, port, user, passwd, db
import jinja2
import re
import cPickle as p
import sys
import os
import glob as g
import random as rand
sys.path.append("app/crawlers")
import dbWrapper as dbW
import numpy as np
import subprocess as sbp
from time import sleep, tzset
import logging
from os import environ
import mapHelper 
import density
import myFunctions


environ['TZ'] = 'UTC+7:00'
tzset()



# logging
logging.basicConfig(filename='logcraig.log', \
            format='%(asctime)s %(message)s',\
            datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)


@app.route('/', methods= ['GET', 'POST'])
def home():
    """Main page requests a state"""
    var_dict = {}
    # user input these parameters from the dropdown of the main page,
    # mainly two states are avaialable for now. 
    state = request.args.get('state')
    var_dict["state"] = state # state will be passed on to cities
    return render_template('main.html', var_dict = var_dict)


@app.route('/cities', methods=['GET', 'POST'])
def cities():
    """Receives user input for state and redirects for
        city selection"""
    state = ''
    # parse user input from form.
    if request.form['submit'] == 'Nevada':
        state = 'Nevada'.lower()
    elif request.form['submit'] == 'California':
        state = 'California'.lower()


    try:
        cities_dict = p.load(open("app/cities.p", "rb"))
        cities = cities_dict[state]
    except Exception as e:
        cities = ["return home"]
        return render_template('cities_err.html', cities = cities)
    logging.info("cities for state {0}".format(state))
    return render_template('cities.html', cities = cities)

 
@app.route('/showTables/<filter_query>', methods=['GET', 'POST'])
def showTables(filter_query):
    """ Show table, filter the table or not. 
        This leads to two options, see the distribution, 
        or do the prediction """

    identifier = ''.join([str(rand.randint(0,9)) for _ in xrange(10)]) # for all Postings
    try:
        city = request.args.get('city')
        sort_value = request.args.get('sort')
        logging.info("city (inner try ST) = " + city)
        logging.info("identifier (inner try ST) = " + identifier)
    except:
        sort_value, city = request.args.get('sort').split('|')
        logging.info("city (outer try ST) = " + city)
        logging.info("identifier (outer try ST) = " + identifier)
        logging.info("sort value (outer try ST) = " + sort_value)

    # Refer to the database, to find the city and postings
    try:
        dbObj = dbW.dbWrapper()
        cmd = "select *  from %s group by title;" % (city)
        knownPostings = dbObj.query(cmd)
    except Exception as e:
        logging.exception(e)
        knownPostings = []


    try:

        # user input these parameters in showTable
        sublet_type = request.args.get('type')
        sublet_rate = request.args.get('rate')
        laundry =request.args.get('laundry')
        quiet = request.args.get('quiet')
        parking = request.args.get('parking')
        minPrice = request.args.get('minPrice')
        maxPrice = request.args.get('maxPrice')

        if not sublet_type:
            sublet_type = "all type"
        if not sublet_rate:
            sublet_rate = "all rate"
        if not sort_value:
            sort_value = "DESC"
        if not quiet:
            quiet = "none"
        if not parking:
            parking = "none"
        if not laundry:
            laundry = "none"
        if not minPrice:
            minPrice = 0
        if not maxPrice:
            maxPrice = 5000

    except Exception as e:
        logging.exception(e)

    try:
        var_dict = {}
        var_dict["thistype"] = sublet_type
        var_dict["thisrate"] = sublet_rate
        var_dict["sort"] = sort_value

        var_dict["quiet"] = quiet
        var_dict["parking"] = parking
        var_dict["laundry"] = laundry
        var_dict["city"] = city
        var_dict["minPrice"] = float(minPrice)
        var_dict["maxPrice"] = float(maxPrice)
        var_dict["identifier"] = identifier

    except Exception as e:
        logging.exception(e)

    allPostings, displayPostings, priceList =  myFunctions.sortposts(knownPostings, var_dict)

    allinfo = {}
    allinfo["allPostings"] = allPostings
    allinfo["displayPostings"]  = displayPostings
    allinfo["priceList"] = priceList
    allinfo["city"] = city
    try:
        with open(identifier + '.p', 'w') as Fout:
            p.dump(allinfo, Fout)
    except Exception as e:
        logging.exception(e)
    try:
        return render_template('showTables.html', postings=displayPostings, var_dict=var_dict )
    except Exception as e:
        logging.exception(e)



@app.route('/genDistribution/<predictionVars>', methods = ['GET', 'POST'])
def genDistribution(predictionVars):

    try:
        identifier = request.args.get('identifier')
        logging.info("cityIdentifer (genDistribution): " + identifier)
        if not identifier:
            logging.debug("cityIdentifer (genDistribution after fail): " + identifier)
            return render_template('main.html')
        try:
            with open(identifier + '.p', 'r') as Fin:
                cityname = p.load(Fin)['city']
        except Exception as e:
            logging.debug("cityIdentifer (genDistribution after fail): " + identifier)
            logging.exception(e)
            cityname = ''
        distribution = "histo_{0}.png".format(cityname)
        movie = "movie_{0}.gif".format(cityname)
        figs = {"distribution": distribution, "movie":movie}
        return render_template('distribution.html', figs = figs )
    except Exception as e:
        logging.debug("cityIdentifer (genDistribution after fail): " + identifier)
        logging.exception(e)
        return render_template('main.html')

@app.route('/interactiveMap/<predictionVars>', methods = ['GET', 'POST'])
def interactiveMap(predictionVars):
    identifier =request.args.get('identifier')
    try:
        with open(identifier + '.p', 'r') as Fin:
            displayPostings = p.load(Fin)['displayPostings']
    except Exception as e:
        logging.exception(e)

    Lngs = []
    Lats = []
    for post in displayPostings:
        Lngs.append(post["lng"])
        Lats.append(post["lat"])
    centerLon, centerLat, zoom = mapHelper.center_zoom(Lngs, Lats)
    mapInfo = {"centerLon": centerLon, "centerLat": centerLat, "zoom": zoom}
    return render_template('showInteractive.html', postings = displayPostings, mapInfo=mapInfo)

@app.route('/interactivePrediction/<predictionVars>', methods = ['GET', 'POST'])
def interactivePrediction(predictionVars):
    """renders the interactive heat map. """

    try:
        identifier = request.args.get('identifier')
        minPrice = float(request.args.get('minPrice'))
        maxPrice = float(request.args.get('maxPrice'))
        try:
            with open(identifier + '.p', 'r') as Fin:
                allPostings = p.load(Fin)['allPostings']
        except Exception as e:
            logging.exception(e)

        Lngs = []
        Lats = []
        postings = []
        for post in allPostings:
            Lngs.append(post["lng"])
            Lats.append(post["lat"])
            postings.append([post["lng"], post["lat"], post["price"]])
        centerLon, centerLat, zoom = mapHelper.center_zoom(Lngs, Lats)
        logging.info("length of postings: " + str(len(postings)))
        predictionData =  density.GaussianPredictor(postings, 32, minPrice,\
                                                    maxPrice, 20)
        logging.info("length of predictionData: " + str(len(predictionData)))
        mapInfo = {"centerLon": centerLon, "centerLat": centerLat,"zoom": zoom}

        return render_template('showInteractiveNew.html', postings = predictionData, mapInfo=mapInfo)
    except Exception as e:
        logging.exception(e)
        return render_template('main.html')


@app.route('/slides', methods= ['GET'])
def slides(): 
    return render_template('slides.html')


