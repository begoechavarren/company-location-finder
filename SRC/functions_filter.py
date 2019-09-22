import numpy as np
import pandas as pd
from pymongo import MongoClient
import time
import requests
from dotenv import load_dotenv
import os
from sklearn import preprocessing
import folium
from folium.plugins import MeasureControl
import webbrowser
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
# https://developers.google.com/places/web-service/get-api-key
# https://console.cloud.google.com/billing/0163C0-E6306C-B76C83?project=project-ironhack-pymongo
# https://developers.google.com/calendar/v3/pagination


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

# functions final df and plot


def create_plot_df(hostelry, service, events, coord):
    google_key = os.getenv("google_key")
    meetup_key = os.getenv("meetup_key")
    data_h = getGoogledata(hostelry, 1500, coord, google_key)
    hostelry_df = pd.DataFrame({"hostelry": [
                               [w['geometry']['location']['lat'], w['geometry']['location']['lng']] for w in [y for x in data_h for y in x]]})
    data_s = getGoogledata(service, 1500, coord, google_key)
    services_df = pd.DataFrame({"services": [
                               [w['geometry']['location']['lat'], w['geometry']['location']['lng']] for w in [y for x in data_s for y in x]]})
    companies_df = pd.DataFrame({'companies': [[x['position']['coordinates'][1], x['position']['coordinates'][0]]
                                               for x in getCompaniesNear(coord[1], coord[0], max_meters=2000)]})
    events_df = pd.DataFrame(
        {"events": getMeetupdata(coord, events, meetup_key)})
    final_df = pd.concat(
        [hostelry_df, services_df, companies_df, events_df], axis=1, sort=False)
    return final_df


def create_folium(df, coords):
    coords = [coords[1], coords[0]]
    icons = {'hostelry': {'color': "blue", 'iconname': "fa-cutlery"}, 'services': {'color': "purple", 'iconname': "fa-asterisk"},
             'companies': {'color': "red", 'iconname': "fa-building"}, 'events': {'color': "green", 'iconname': "fa-calendar-o"}}
    map_folium = folium.Map(coords, width=750, height=500, zoom_start=17)
    folium.CircleMarker(
        coords, radius=9, fill_color="#F35C50").add_to(map_folium)
    for e in df:
        for coord in df[e]:
            if coord != coords:
                try:
                    folium.Marker(coord, radius=9, icon=folium.Icon(
                        color=icons[e]['color'], prefix='fa', icon=icons[e]['iconname']), fill_color="#F35C50").add_to(map_folium)
                except:
                    pass
    map_folium.add_child(MeasureControl())
    # save map as html
    map_folium.save('./map_folium.html')
    return map_folium


def open_folium_browser():
    new = 2  # open in a new tab, if possible
    url = "file:///{}{}".format(os.getcwd(), "/map_folium.html")
    webbrowser.open(url, new=new)


def get_address(lat, lng):
    google_key = os.getenv("google_key")
    url = "https://maps.googleapis.com/maps/api/geocode/json?latlng={},{}&key={}".format(
        lat, lng, google_key)
    data = [(requests.get(url)).json()]
    address = data[0]['results'][0]['formatted_address']
    return address
