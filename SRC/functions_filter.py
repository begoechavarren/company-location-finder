import pandas as pd
import requests
from dotenv import load_dotenv
import os
from sklearn import preprocessing
import folium
from folium.plugins import MeasureControl
import webbrowser
import os
from branca.element import Template, MacroElement
from pathlib import Path
from functions_process import getGoogledata, getCompaniesNear, getMeetupdata


# functions punctuation
def normalize_df(df):
    df.set_index('coords', inplace=True)
    x = df.values  # returns a numpy array
    min_max_scaler = preprocessing.MinMaxScaler()
    x_scaled = min_max_scaler.fit_transform(x)
    new_df = pd.DataFrame(x_scaled)
    new_df.columns = ["near_companies", "hostelry", "services", "events"]
    return new_df


def punctuation(n_df, df, b_near_companies, b_hostelry, b_services, b_events):
    df['near_companies'] = list(n_df['near_companies'])
    df['hostelry'] = list(n_df['hostelry'])
    df['services'] = list(n_df['services'])
    df['events'] = list(n_df['events'])
    df['punctuation'] = df['near_companies']*b_near_companies + \
        df['hostelry']*b_hostelry+df['services'] * \
        b_services+df['events']*b_events
    final_location = df[df['punctuation'] == max(df['punctuation'])].index[0]
    return final_location

# functions final df and plot


def create_plot_df(hostelry, service, events, coord):
    google_key = os.getenv("google_key")
    meetup_key = os.getenv("meetup_key")
    data_h = getGoogledata(hostelry, "2000", coord, google_key)
    hostelry_df = pd.DataFrame({"hostelry": [
                               [x['geometry']['location']['lat'], x['geometry']['location']['lng']] for x in data_h]})
    data_s = getGoogledata(service, "2000", coord, google_key)
    services_df = pd.DataFrame({"services": [
                               [x['geometry']['location']['lat'], x['geometry']['location']['lng']] for x in data_s]})
    companies_df = pd.DataFrame({'companies': [[x['position']['coordinates'][1], x['position']['coordinates'][0]]
                                               for x in getCompaniesNear(coord[1], coord[0], max_meters=2000)]})
    events_df = pd.DataFrame(
        {"events": getMeetupdata(coord, events, meetup_key)})
    final_df = pd.concat(
        [hostelry_df, services_df, companies_df, events_df], axis=1, sort=False)
    return final_df


def get_address(lat, lng):
    google_key = os.getenv("google_key")
    url = "https://maps.googleapis.com/maps/api/geocode/json?latlng={},{}&key={}".format(
        lat, lng, google_key)
    data = [(requests.get(url)).json()]
    address = data[0]['results'][0]['formatted_address']
    return address


def create_folium(df, coords):
    address = get_address(coords[1], coords[0])
    coords = [coords[1], coords[0]]
    icons = {'hostelry': {'color': "orange", 'iconname': "fa-cutlery"}, 'services': {'color': "blue", 'iconname': "fa-asterisk"},
             'companies': {'color': "darkpurple", 'iconname': "fa-building"}, 'events': {'color': "green", 'iconname': "fa-calendar-o"}}
    map_folium = folium.Map(coords, width=1000, height=700, zoom_start=17)
    folium.CircleMarker(coords, radius=9, color="#DA1212").add_to(map_folium)
    for e in df:
        for coord in df[e]:
            if coord != coords:
                try:
                    folium.Marker(coord, radius=9, icon=folium.Icon(
                        color=icons[e]['color'], prefix='fa', icon=icons[e]['iconname']), fill_color="#F35C50").add_to(map_folium)
                except:
                    pass
    map_folium.add_child(MeasureControl())
    folium.TileLayer('cartodbpositron').add_to(map_folium)
    tooltip = 'Click me!'
    folium.Marker(coords, popup='<i>{}</i>'.format(address), icon=folium.Icon(
        color='red', prefix='fa', icon="fa-circle"), tooltip=tooltip).add_to(map_folium)
    return map_folium


def create_legend(folium_object, service, events, hostelry):
    template = """
    {% macro html(this, kwargs) %}

    <!doctype html>
    <html lang="en">
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <title>jQuery UI Draggable - Default functionality</title>
      <link rel="stylesheet" href="//code.jquery.com/ui/1.12.1/themes/base/jquery-ui.css">

      <script src="https://code.jquery.com/jquery-1.12.4.js"></script>
      <script src="https://code.jquery.com/ui/1.12.1/jquery-ui.js"></script>

      <script>
      $( function() {
        $( "#maplegend" ).draggable({
                        start: function (event, ui) {
                            $(this).css({
                                right: "auto",
                                top: "auto",
                                bottom: "auto"
                            });
                        }
                    });
    });

      </script>
    </head>
    <body>


    <div id='maplegend' class='maplegend' 
        style='position: absolute; z-index:9999; border:2px solid grey; background-color:rgba(255, 255, 255, 0.8);
         border-radius:6px; padding: 10px; font-size:14px; right: 470px; bottom: 100px;'>

    <div class='legend-title'>Legend</div>
    <div class='legend-scale'>
      <ul class='legend-labels'>
        <li><span style='background:#400D79;opacity:0.7;'></span>Companies</li>
        <li><span style='background:#3386FF;opacity:0.7;'></span>"""+service.title()+"""s</li>
        <li><span style='background:#158E34;opacity:0.7;'></span>"""+events.title()+""" events</li>
        <li><span style='background:#F97100;opacity:0.7;'></span>"""+hostelry.title()+"""</li>

      </ul>
    </div>
    </div>

    </body>
    </html>

    <style type='text/css'>
      .maplegend .legend-title {
        text-align: left;
        margin-bottom: 5px;
        font-weight: bold;
        font-size: 90%;
        }
      .maplegend .legend-scale ul {
        margin: 0;
        margin-bottom: 5px;
        padding: 0;
        float: left;
        list-style: none;
        }
      .maplegend .legend-scale ul li {
        font-size: 80%;
        list-style: none;
        margin-left: 0;
        line-height: 18px;
        margin-bottom: 2px;
        }
      .maplegend ul.legend-labels li span {
        display: block;
        float: left;
        height: 16px;
        width: 30px;
        margin-right: 5px;
        margin-left: 0;
        border: 1px solid #999;
        }
      .maplegend .legend-source {
        font-size: 80%;
        color: #777;
        clear: both;
        }
      .maplegend a {
        color: #777;
        }
    </style>
    {% endmacro %}"""

    macro = MacroElement()
    macro._template = Template(template)

    folium_object.get_root().add_child(macro)
    folium_object.save('../output/map_folium.html')  # save map as html
    return folium_object


def open_folium_browser(folium_object):
    new = 2  # open in a new tab, if possible
    url = "file://{}{}{}".format(str(Path(os.getcwd()).parent),
                                 "/output", "/{}.html".format(folium_object))
    webbrowser.open(url, new=new)
