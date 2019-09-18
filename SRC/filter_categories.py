from functions_filter import *
from pymongo import MongoClient
import pandas as pd
from clean import companies, coord_list

# get the cleaned database from mongo
client = MongoClient('mongodb://localhost:27017/')
db = client.companies

# filter by category and money raised
# !!!!!!!!!!!cat_regex y min_money_raised deberían venir de los argumentos!!!! (por ahora los defino)
cat_regex = "(?i)tech|(?i)web|(?i)design|(?i)code|(?i)mobile|(?i)advertising"
min_money_raised = 1000000
selected = db.selected.find({"$and": [{"total_money_raised": {"$gte": min_money_raised}},
                                      {"$or": [{"tag_list": {"$regex": cat_regex}}, {"category_code": {"$regex": cat_regex}}, {"name": {"$regex": cat_regex}}, {"description": {"$regex": cat_regex}}, {"overview": {"$regex": cat_regex}}]}]})
selected_df = pd.DataFrame(selected)

# create dataframe based on coords which have more companies of the selected category next to them
my_df = df_creator(coord_list)
