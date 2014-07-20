#!/usr/bin/env python

import logging
import numpy as np

def sortposts(knownPostings, var_dict):

    priceList = []
    allPostings = []
    tmpPostings = []
    displayPostings = []
    for entry in knownPostings:
        # Save all postings
        try:
                posting_dict0 = {}
                posting_dict0["price"]  = entry[4]
                posting_dict0["lat"] = entry[5]
                posting_dict0["lng"] = entry[6]

        except Exception as e:
            logging.exception(e)

        try:
                allPostings.append(posting_dict0)

        except Exception as e:
            logging.exception(e)

        try:
            # there are five conditions:
            typeBool = False
            parkBool = False
            rateBool = False
            quietBool = False
            laundryBool = False
            minPriceBool = False
            maxPriceBool = False
            activeBool = False

            # we need all of the conditions to be true if we
            # are going to add it. 

            # deal with type filter
            if var_dict["thistype"] == "all type":
                typeBool = True
            elif entry[2] == var_dict["thistype"]:
                typeBool = True

            # deal with rate filter
            if var_dict["thisrate"] == "all rate":
                rateBool = True
            elif entry[3] == var_dict["thisrate"]:
                rateBool = True

            # deal with quiet filter
            if var_dict["quiet"] =="none":
                quietBool = True
            elif entry[10] == var_dict["quiet"]:
                quietBool = True

            # deal with parking filter
            if var_dict["parking"] =="none":
                parkBool = True
            elif entry[9] == var_dict["parking"]:
                parkBool = True

            # deal with laundry filter
            if var_dict["laundry"] =="none":
                laundryBool = True
            elif entry[11] == var_dict["laundry"]:
                laundryBool = True

            # deal with price range
            if var_dict["minPrice"] ==0:
                minPriceBool = True
            elif entry[4] >= var_dict["minPrice"]:
                minPriceBool = True

            if var_dict["maxPrice"] ==0:
                maxPriceBool = True
            elif entry[4] <= var_dict["maxPrice"]:
                maxPriceBool = True

            if entry[12] == "yes":
                activeBool = True
            if typeBool and parkBool and rateBool and quietBool and \
                    laundryBool and minPriceBool and maxPriceBool and activeBool:

                posting_dict = {}
                posting_dict["postingID"] = entry[0]
                posting_dict["link"] = entry[1]
                posting_dict["type"]  = entry[2]
                posting_dict["rate"]  = entry[3]
                posting_dict["price"]  = entry[4]
                posting_dict["lat"] = entry[5]
                posting_dict["lng"] = entry[6]
                posting_dict["title"] = entry[7]
                posting_dict["postbody"] = entry[8]

                posting_dict["parking"] = entry[9]
                posting_dict["quiet"] = entry[10]
                posting_dict["laundry"] = entry[11]

                tmpPostings.append( posting_dict )
                priceList.append( entry[4] )
        except Exception as e:
            logging.exception(e)


    # condition for sorting descend
    logging.info( var_dict["sort"] )
    if var_dict["sort"] == "DESC":
        for index in np.argsort(priceList)[::-1]:
           if priceList[index] < 10.**4 and priceList[index] > 0:#40.:
                displayPostings.append(tmpPostings[index])
    else:
        for index in np.argsort(priceList):
            if priceList[index] < 10.**4 and priceList[index] > 0.:
                displayPostings.append(tmpPostings[index])
    allPostings.append(posting_dict0)
    return allPostings, displayPostings, priceList

