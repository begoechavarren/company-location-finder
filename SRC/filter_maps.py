from functions_filter import *
from filter_categories import my_df
from dotenv import load_dotenv
import os

load_dotenv()

google_key = os.getenv("google_key")


# ojo esto hacerlo con parámetros!
# y ojo palabras que meta el usuario que sean separadas con comas

my_df['hostelry'] = my_df.apply(lambda x: create_hostelry(
    "starbucks", 1500, x["coords"], google_key), axis=1)

my_df['services'] = my_df.apply(lambda x: create_hostelry(
    "elementary school", 1500, x["coords"], google_key), axis=1)
