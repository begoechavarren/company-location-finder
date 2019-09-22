import pandas as pd
import pymongo
from pymongo import MongoClient
import numpy as np
import re
from functions_clean import *
import json
import os

# import collection to pymongo

# alternative (bash): mongoimport --db companies --collection companies --file companies.json
bashCommand = 'mongoimport --db companies --collection companies --file ../input/companies.json'
try:
    os.system(bashCommand)
except:
    pass

# data acquisition from pymongo
client = MongoClient("mongodb://localhost:27017/")
db = client.companies

companies = db.companies.find()
data_companies = pd.DataFrame(companies)
companies = db.companies.find({"$and": [
    {"offices": {"$exists": True}},
    {"offices": {"$ne": None}},
    {"$and": [{"offices.latitude": {"$exists": True}},
              {"offices.longitude": {"$exists": True}}]},
    {"category_code": {"$exists": True}},
    {"category_code": {"$ne": None}},
    {"founded_year": {"$exists": True}},
    {"founded_year": {"$gte": 2003}},
    {"deadpooled_year": None},
    {"number_of_employees": {
        "$exists": True}},
    {"number_of_employees": {"$gte": 10}},
    {"total_money_raised": {
        "$exists": True}},
    {"total_money_raised": {"$ne": None}},
    {"total_money_raised": {"$not": {"$size": 0}}},

]
},
    {"_id": 0, "crunchbase_url": 0, "products": 0,
     "acquisition": 0, "acquisitions": 0, "video_embeds": 0,
     "screenshots": 0, "external_links": 0, "partners": 0,
     "image": 0,
     'deadpooled_day': 0, 'deadpooled_month': 0,
     'deadpooled_url': 0, 'deadpooled_year': 0,
     }
)
companies = pd.DataFrame(companies)

# stacking various offices in different rows
offices = companies.set_index('name').offices.apply(
    pd.Series).stack().reset_index(level=-1, drop=True).reset_index()
offices.columns = ['name', 'office']
companies = companies.drop('offices', 1)
companies = companies.merge(offices, on='name', how='outer')

# add geopoint
companies['lat'] = companies['office'].apply(createLat)
companies['long'] = companies['office'].apply(createLon)
companies.dropna(subset=['lat', 'long'], inplace=True)
companies['position'] = companies.apply(createGeoJson, axis=1)


# currency converter
converter = authRequest(
    'https://api.exchangeratesapi.io/latest?base=USD')['rates']
companies['total_money_raised'] = companies.apply(lambda df: currencyconverter(df['total_money_raised'], converter),
                                                  axis=1)

# create coordinates list
coord_list = coord_list_creator(companies)

# export to json
companies.to_json('../output/cleaned_companies.json', orient="records")

# import to mongoDB and create 2dSphere index
# alternative (bash): mongoimport --db companies --collection selected --jsonArray offices.json

mycol = db["selected"]

try:
    mycol.drop()
except Exception as e:
    print("Collection does not exist.")

mycol.insert_many(companies.to_dict('records'))
mycol.create_index([('position', pymongo.GEOSPHERE)])
