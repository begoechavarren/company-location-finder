import numpy as np
import pandas as pd
from pymongo import MongoClient
import time
import requests
from dotenv import load_dotenv
import os


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


def getGoogledata(place, radius, coord, key):
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={},{}&radius={}&keyword={}&key={}".format(
        str(coord[1]), str(coord[0]), str(radius), place, key)
    data = [(requests.get(url)).json()]
    while "next_page_token" in data[-1]:
        new_url = url+"&pagetoken={}".format(data[-1]['next_page_token'])
        time.sleep(2)
        new_req = (requests.get(str(new_url))).json()
        data.append(new_req)
    total_results = []
    for x in data:
        total_results.append(x['results'])
    return total_results


def countGoogledata(place, radius, coord, key):
    return len(getGoogledata(place, radius, coord, key))


def create_hostelry(place, radius, coord, key):
    count = countGoogledata(place, radius, coord, key)
    return count


def filter_maps(df, hostelry, services):
    load_dotenv()
    google_key = os.getenv("google_key")
    df['hostelry'] = df.apply(lambda x: create_hostelry(
        hostelry, 1500, x["coords"], google_key), axis=1)
    df['services'] = df.apply(lambda x: create_hostelry(
        services, 1500, x["coords"], google_key), axis=1)
    return df


# functions filter_meetup
def getMeetupdata(coord, category, key):
    categories = {'outdoors-adventure': '242', 'tech': '292', 'parents-family': '232', 'health-wellness': '302', 'sports-fitness': '282', 'education': '562', 'photography': '262', 'food': '162', 'writing': '582', 'language': '212', 'music': '512',
                  'movements': '552', 'lgbtq': '585', 'film': '583', 'games-sci-fi': '182', 'beliefs': '132', 'arts-culture': '122', 'book-clubs': '222', 'dancing': '542', 'pets': '252', 'hobbies-crafts': '532', 'fashion-beauty': '584', 'social': '272', 'career-business': '522'}
    category = categories[category]
    url = "https://api.meetup.com/find/upcoming_events?&sign=true&photo-host=public&lon={}&topic_category={}&lat={}&key={}&sign=true".format(
        str(coord[0]), category, str(coord[1]), key)
    result = ((requests.get(url)).json())['events']
    data = []
    for x in result:
        try:
            data.append([x['venue']['lat'], x['venue']['lon']])
        except:
            pass
    return data


def countMeetupdata(coord, category, key):
    return len(getMeetupdata(coord, category, key))


def filter_meetup(category, df):
    load_dotenv()
    meetup_key = os.getenv("meetup_key")
    df['events'] = df.apply(lambda x: countMeetupdata(
        x["coords"], category, meetup_key), axis=1)
    return df
