import numpy as np
import pandas as pd
from pymongo import MongoClient
import time
import requests

# functions filter_categories


def categories_builder(txt):
    regex = ""
    categories = [cat.strip() for cat in txt.split(",")]
    for e in categories:
        regex += "(?i){}|".format(e)
    return regex[:-1]


def getCompaniesNear(lat, long, max_meters=2000):
    client = MongoClient("mongodb://localhost:27017/")
    db = client.companies
    return list(db.selected.find({
        "position": {
            "$near": {
                "$geometry": {
                    "type": "Point",
                    "coordinates": [long, lat]
                },
                "$maxDistance": max_meters
            }
        }
    }))


def df_creator(lst_coord):
    lst_near = []
    for x in lst_coord:
        lst_near.append([x, len(getCompaniesNear(x[1], x[0]))])
    lst_near.sort(key=lambda x: x[1], reverse=True)
    q = np.quantile([x[1] for x in lst_near], .93)
    df_list = [x for x in lst_near if x[1] >= q]
    df = pd.DataFrame(df_list, columns=["coords", "near_companies"])
    return df

# functions filter_maps
# https://developers.google.com/places/web-service/get-api-key
# https://console.cloud.google.com/billing/0163C0-E6306C-B76C83?project=project-ironhack-pymongo
# https://developers.google.com/calendar/v3/pagination


def countGoogledata(place, radius, coord, key):
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={},{}&radius={}&keyword={}&key={}".format(
        str(coord[1]), str(coord[0]), str(radius), place, key)
    data = [(requests.get(url)).json()]
    while "next_page_token" in data[-1]:
        new_url = url+"&pagetoken={}".format(data[-1]['next_page_token'])
        time.sleep(2)
        new_req = (requests.get(str(new_url))).json()
        data.append(new_req)
    total_results = 0
    for x in data:
        total_results += len(x['results'])
    return total_results


def create_hostelry(place, radius, coord, key):
    count = countGoogledata(place, radius, coord, key)
    print(count)
    return count


# functions filter_meetup
def countMeetupdata(coord, category, key):
    url = "https://api.meetup.com/find/upcoming_events?&sign=true&photo-host=public&lon={}&topic_category={}&lat={}&key={}&sign=true".format(
        str(coord[0]), category, str(coord[1]), key)
    data = (requests.get(url)).json()
    count = len([x['id'] for x in data['events']])
    print(count)
    return count
