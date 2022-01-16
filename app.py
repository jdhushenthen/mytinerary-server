from flask import Flask, Response, send_from_directory, send_file
from flask_cors import CORS
import requests
import json
import random
from datetime import datetime
from pdf_gen import create_pdf
from ics_gen import create_ics
import os

random.seed(datetime.now())
API_KEY = 'rZz4DQe06UyMRcTToBVyQrOrkltbyZ5F8MvO3yW8vadGOo41iG8PZKoi_-HWV4p7LVSIOnXIctifKNQf_1sSsmbP1RkWKnAufcpA5p65jU4a4zSmqX03dzP_cfPgYXYx'

app = Flask(__name__)
CORS(app)

class Busyness:
    RELAXED, MODERATE, BUSY = range(3)

def filter_categories(categories):
    has_restaurant = has_nightlife = False

    if "Restaurants" in categories:
        has_restaurant = True
        categories.remove("Restaurants")
    
    if "Nightlife" in categories:
        has_nightlife = True
        categories.remove("Nightlife")
    
    return has_restaurant, has_nightlife

def search_businesses(category, location, ids):
    url = "https://api.yelp.com/v3/businesses/search" + "?term=" + category + "&location=" + location + "&radius=3000"    
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Authorization': 'Bearer ' + API_KEY,
        'Content-Type': 'application/json',
    }
    res = requests.get(url, headers = headers).json()
    
    obj = None

    for business in res["businesses"]:
        if business['id'] not in ids:

            ids.add(business['id'])
            obj = {
                "name": business["name"],
                "review_count": business["review_count"],
                "rating": business["rating"],
                "location": ", ".join(business["location"]["display_address"]),
                "phone": business["phone"]
            }
            break

    return obj

@app.route('/api/post/<string:startDate>/<string:endDate>/<string:userLocation>/<string:userCategories>/<int:userBusyness>/')
def generate_itinerary(startDate, endDate, userLocation, userCategories, userBusyness):
    start = startDate.replace('-', ' ')
    end = endDate.replace('-', ' ')
    startTime = datetime.strptime(start, '%b %d %Y')
    endTime = datetime.strptime(end, '%b %d %Y')
    num_days = (endTime-startTime).days
    days_itin = []
    location = userLocation
    #categories = ["Parks", "Shopping", "Restaurants", "Nightlife", "Entertainment"]
    categories = userCategories.split('-')
    busyness = userBusyness
    has_restaurant, has_nightlife = filter_categories(categories)
    last_location = location
    ids = set()
    itinerary = {"activity1" : None, "lunch" : None, "activity2" : None, "activity3" : None, "dinner" : None, "night" : None}

    for i in range(num_days):
        last_location = location
        itinerary = {"activity1" : None, "lunch" : None, "activity2" : None, "activity3" : None, "dinner" : None, "night" : None}

        # ACTIVITY 1
        if busyness != Busyness.RELAXED and len(categories) > 0:
            rand = random.randint(0, len(categories) - 1)
            category = categories[rand]
            itinerary["activity1"] = search_businesses(category, last_location, ids)
        
            last_location = itinerary["activity1"]["location"]
    
        # LUNCH
        if has_restaurant:
            category = "Restaurants"
            itinerary["lunch"] = search_businesses(category, last_location, ids)
        
            last_location = itinerary["lunch"]["location"]

        # ACTIVITY 2
        if len(categories) > 0:
            rand = random.randint(0, len(categories) - 1)
            category = categories[rand]
            itinerary["activity2"] = search_businesses(category, last_location, ids)
            
            last_location = itinerary["activity2"]["location"]

        # ACTIVITY 3
        if busyness == Busyness.BUSY and len(categories) > 0:
            rand = random.randint(0, len(categories) - 1)
            category = categories[rand]
            itinerary["activity3"] = search_businesses(category, last_location, ids)
        
            last_location = itinerary["activity3"]["location"]

        # DINNER
        if has_restaurant:
            category = "Restaurants"
            itinerary["dinner"] = search_businesses(category, last_location, ids)
        
            last_location = itinerary["dinner"]["location"]

        # NIGHTLIFE
        if has_nightlife:
            category = "Nightlife"
            itinerary["night"] = search_businesses(category, last_location, ids)
        
            last_location = itinerary["night"]["location"]

        days_itin.append(itinerary)

    print(days_itin)
    create_ics(days_itin, startTime)
    create_pdf(days_itin, startTime, num_days)
    data = {"days_itin": days_itin}
    return data

@app.route('/api/get/itinerary/pdf')
def get_pdf():
    workingdir = os.path.abspath(os.getcwd())
    return send_file(os.path.join(workingdir, 'pdfTable.pdf'), as_attachment=True)

@app.route('/api/get/itinerary/ics')
def get_ics():
    workingdir = os.path.abspath(os.getcwd())
    return send_file(os.path.join(workingdir, 'example.ics'), as_attachment=True)
