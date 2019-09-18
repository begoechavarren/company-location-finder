from filter_maps import my_df
from functions_filter import *
from dotenv import load_dotenv
import os
from sklearn import preprocessing

load_dotenv()

meetup_key = os.getenv("meetup_key")

# ojo cambiar la categoría con inputs!!!!!
my_df['events'] = my_df.apply(lambda x: countMeetupdata(
    x["coords"], "562", meetup_key), axis=1)

# create normalized df
my_df.set_index('coords', inplace=True)
x = my_df.values  # returns a numpy array
min_max_scaler = preprocessing.MinMaxScaler()
x_scaled = min_max_scaler.fit_transform(x)
df = pd.DataFrame(x_scaled)
df.columns = ["near_companies", "hostelry", "services", "events"]
my_df['near_companies'] = list(df['near_companies'])
my_df['hostelry'] = list(df['hostelry'])
my_df['services'] = list(df['services'])
my_df['events'] = list(df['events'])

b_near_companies = 1
b_hostelry = 2
b_services = 4
b_events = 3
my_df['punctuation'] = my_df['near_companies']*b_near_companies + \
    my_df['hostelry']*b_hostelry+my_df['services'] * \
    b_services+my_df['events']*b_events

final_location = my_df[my_df['punctuation']
                       == max(my_df['punctuation'])].index[0]


print(final_location)
