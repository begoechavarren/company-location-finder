from dotenv import load_dotenv
from functions_filter import *
from filter_categories import my_df
import os

load_dotenv()

google_key = os.getenv("google_key")

my_df['hostelry'] = my_df.apply(lambda x: create_hostelry(
    "starbucks", 1500, x["coords"], google_key), axis=1)

print(my_df)
