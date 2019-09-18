import requests
import re


def createLat(office):
    return office['latitude']


def createLon(office):
    return office['longitude']


def createGeoJson(office):
    return {
        "type": "Point",
        "coordinates": [office["long"], office["lat"]]
    }


def authRequest(url):
    response = requests.get("{}".format(url))
    return response.json()


def currencyconverter(txt, converter):
    txt = [float(re.sub("[^0-9.]", "", txt)), re.sub("[0-9.]", "", txt)]
    abrev = {"M": "million", "B": "billion", "kr": "SEK",
             "k": "thousand", "€": "EUR", "£": "GBP", "C$": "CAD", "$": ""}
    scales = {"billion": 1000000000, "million": 1000000, "thousand": 1000}
    currencies = {"kr": "SEK", "€": "EUR", "£": "GBP", "C$": "CAD"}
    for k, v in abrev.items():
        txt[1] = txt[1].replace(k, v)
    for k, v in scales.items():
        if k in txt[1]:
            txt[0] = txt[0] * v
    for v in list(currencies.values()):
        if v in txt[1]:
            txt[0] = txt[0]/converter[v]
    return int(txt[0])


def coord_list_creator(df):
    coord_list = []
    coord_shortlist = []
    for i in range(len(df.index)):
        coord = [df.iloc[i]["position"]['coordinates']
                 [0], df.iloc[i]["position"]['coordinates'][1]]
        coord_short = [round(df.iloc[i]["position"]['coordinates'][0]), round(
            df.iloc[i]["position"]['coordinates'][1])]
        if coord_short not in coord_shortlist:
            coord_list.append(coord)
            coord_shortlist.append(coord_short)
    return coord_list
