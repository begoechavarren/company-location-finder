import numpy as np
import pandas as pd
from pymongo import MongoClient
import time
import requests
from dotenv import load_dotenv
import os
from sklearn import preprocessing


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


def filter_categories(companies, coord_list, min_money_raised, cat_regex):
    # get the cleaned database from mongo
    client = MongoClient('mongodb://localhost:27017/')
    db = client.companies
    # filter by category and money raised
    # !!!!!!!!!!!cat_regex y min_money_raised deberían venir de los argumentos!!!! (por ahora los defino)
    selected = db.selected.find({"$and": [{"total_money_raised": {"$gte": min_money_raised}},
                                          {"$or": [{"tag_list": {"$regex": cat_regex}}, {"category_code": {"$regex": cat_regex}}, {"name": {"$regex": cat_regex}}, {"description": {"$regex": cat_regex}}, {"overview": {"$regex": cat_regex}}]}]})
    selected_df = pd.DataFrame(selected)
    # create dataframe based on coords which have more companies of the selected category next to them
    my_df = df_creator(coord_list)
    return my_df

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
    return count


def filter_maps(df):
    load_dotenv()
    google_key = os.getenv("google_key")
    # importaba my_df
    # ojo esto hacerlo con parámetros!
    # y ojo palabras que meta el usuario que sean separadas con comas
    df['hostelry'] = df.apply(lambda x: create_hostelry(
        "starbucks", 1500, x["coords"], google_key), axis=1)
    df['services'] = df.apply(lambda x: create_hostelry(
        "elementary school", 1500, x["coords"], google_key), axis=1)
    return df


# functions filter_meetup
def countMeetupdata(coord, category, key):
    url = "https://api.meetup.com/find/upcoming_events?&sign=true&photo-host=public&lon={}&topic_category={}&lat={}&key={}&sign=true".format(
        str(coord[0]), category, str(coord[1]), key)
    data = (requests.get(url)).json()
    count = len([x['id'] for x in data['events']])
    return count


def filter_meetup(category, df):
    load_dotenv()
    meetup_key = os.getenv("meetup_key")
    df['events'] = df.apply(lambda x: countMeetupdata(
        x["coords"], category, meetup_key), axis=1)
    return df


# functions punctuation

def normalize_df(df):
    df.set_index('coords', inplace=True)
    x = df.values  # returns a numpy array
    min_max_scaler = preprocessing.MinMaxScaler()
    x_scaled = min_max_scaler.fit_transform(x)
    new_df = pd.DataFrame(x_scaled)
    new_df.columns = ["near_companies", "hostelry", "services", "events"]
    df['near_companies'] = list(df['near_companies'])
    df['hostelry'] = list(df['hostelry'])
    df['services'] = list(df['services'])
    df['events'] = list(df['events'])
    return df


def punctuation(df, b_near_companies, b_hostelry, b_services, b_events):
    df['punctuation'] = df['near_companies']*b_near_companies + \
        df['hostelry']*b_hostelry+df['services'] * \
        b_services+df['events']*b_events
    final_location = df[df['punctuation'] == max(df['punctuation'])].index[0]
    return final_location
