import googlemaps
import requests
import os
from urllib.parse import urlencode
from flask import Flask, render_template,request
from flask_sqlalchemy import SQLAlchemy
import geocoder
gmaps = googlemaps.Client(key="AIzaSyDFyabNVDHz5BxpMXgxH6vb4MdJY9rY0z4")
API_KEY = "AIzaSyDFyabNVDHz5BxpMXgxH6vb4MdJY9rY0z4"
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class user(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(80), nullable=False)

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/work-page',methods=['GET','POST'])
def work():
    if request.method == 'POST':
        location = request.form.get('location')
        entry = user(location=location)
        db.session.add(entry)  # making the database entry
        db.session.commit()

    return render_template('work.html')


@app.route('/events', methods=['GET', 'POST'])
def find_events_nearby():
    """Returns all the events being or going to be held at this location

    Args:
        loc (str): A city or a station

    Returns:
        [type]: list of tuples(information about the event)
        :param loc:
        :param str:
    """
    post = user.query.all()
    last_post = post[-1]
    loc = last_post.location
    params = {
        "engine": "google_events",
        "q": f"Events in {loc}",
        "h1": "en",
        "gl": "us",
        "api_key": "0f01409efdccb44b343b4bb8b8624144676a49b5eb5b6dcfcf75b74120b682f8"
    }

    encoded_params = urlencode(params)
    encoded_url = f'https://serpapi.com/search.json?{encoded_params}'
    events_results = requests.get(encoded_url).json().get('events_results')
    process_key = {
        "title": lambda val: val,
        "address": lambda val: val[0] + val[1],
        "description": lambda val: val,
        "date": lambda val: val.get("when"),
        "ticket_info": lambda val: val[0].get('link'),
        "thumbnail": lambda val: val
    }
    for _ in range(len(events_results)):
        allowed_results = [{key: process_key[key](val) for key, val in event.items()
                            if key in process_key} for event in events_results]

    return render_template('events.html', data=allowed_results)

@app.route('/tourists')
def find_tourist_attraction_places():
    """
    Returns a list of dictionaries containing information about the name, address,
    rating, phone number and image of nearby tourist attraction places.
    """
    post = user.query.all()
    last_post = post[-1]
    place = last_post.location
    lat,lng = find_lat_lng(place)
    radius = 2000
    tourist_places_json = gmaps.places_nearby(
        location=[lat, lng], type="tourist_attraction", radius=radius)

    while not tourist_places_json['results']:
        radius += 500
        tourist_places_json = gmaps.places_nearby(
            location=[lat, lng], type="tourist_attraction", radius=radius)

    results = tourist_places_json['results']

    photo_references = []
    for i in range(len(results)):
        photos_list = results[i]['photos'] if 'photos' in results[i] else None
        if photos_list:
            photos_dict = photos_list[0]
            photo_references.append(photos_dict['photo_reference'])
        else:
            photo_references.append(None)

    places_id = [d.get('place_id') for d in results]

    info = extract_information(places_id)
    images = get_image_urls(photo_references)

    for i in range(len(info)):
        info[i]["image"] = images[i]

    return render_template('tourists.html',info=info)

@app.route('/restaurants')
def find_restaurants():
    """
    Returns a list of dictionaries containing information about the name, address,
    rating, phone number and image of nearby restaurants.
    """
    post = user.query.all()
    last_post = post[-1]
    place = last_post.location
    lat, lng = find_lat_lng(place)
    radius = 1000
    restaurants_json = gmaps.places_nearby(
        location=[lat, lng], type="restaurant", radius=radius)

    while not restaurants_json['results']:
        radius += 500
        restaurants_json = gmaps.places_nearby(
            location=[lat, lng], type="restaurant", radius=radius)

    results = restaurants_json['results']

    photo_references = []
    for i in range(len(results)):
        photos_list = results[i]['photos'] if 'photos' in results[i] else None
        if photos_list:
            photos_dict = photos_list[0]
            photo_references.append(photos_dict['photo_reference'])
        else:
            photo_references.append(None)

    places_id = [d.get('place_id') for d in results]

    info = extract_information(places_id)
    images = get_image_urls(photo_references)

    for i in range(len(info)):
        info[i]["image"] = images[i]

    return render_template('restaurants.html',info=info)

@app.route('/hotels')
def find_hotels():
    """
    Returns a list of dictionaries containing information about the name, address,
    rating, phone number and image of nearby hotels.
    """
    post = user.query.all()
    last_post = post[-1]
    place = last_post.location
    lat, lng = find_lat_lng(place)
    params = {
        "input": "hotel",
        "location": str(lat) + "," + str(lng),
        "radius": 2000,
        "strictbounds": "true",
        "key": API_KEY
    }

    encoded_params = urlencode(params)
    encoded_url = f'https://maps.googleapis.com/maps/api/place/autocomplete/json?{encoded_params}'
    res = requests.get(encoded_url).json()

    places_id = [res["predictions"][i]["place_id"]
                 for i in range(len(res["predictions"]))]
    photo_references = extract_photo_references(places_id)

    info = extract_information(places_id)
    images = get_image_urls(photo_references)

    for i in range(len(info)):
        info[i]["image"] = images[i]

    return render_template('hotels.html',info=info)

@app.route('/hospitals')
def find_hospitals():
    """
    Returns a list of dictionaries containing information about the name, address,
    and phone number of nearby hospitals
    """
    post = user.query.all()
    last_post = post[-1]
    place = last_post.location
    lat, lng = find_lat_lng(place)
    radius = 1000
    hospitals_json = gmaps.places_nearby(
        location=[lat, lng], type="hospital", radius=radius)

    while hospitals_json['results'] == []:
        radius += 500
        hospitals_json = gmaps.places_nearby(
            location=[lat, lng], type="hospital", radius=radius)

    results = hospitals_json['results']
    places_id = [d.get('place_id') for d in results]

    info = extract_information(places_id)
    return render_template('hospitals.html',info=info)

@app.route('/police-stations')
def find_police_stations():
    """
    Returns a list of dictionaries containing information about the name, address,
    phone number of nearby police stations.
    """
    post = user.query.all()
    last_post = post[-1]
    place = last_post.location
    lat, lng = find_lat_lng(place)
    radius = 1000
    police_json = gmaps.places_nearby(
        location=[lat, lng], type="police", radius=radius)

    while not police_json['results']:
        radius += 500
        police_json = gmaps.places_nearby(
            location=[lat, lng], type="police", radius=radius)

    places_id = [d.get('place_id') for d in police_json['results']]

    info = extract_information(places_id)
    return render_template('police-stations.html',info=info)

@app.route('/banks')
def find_banks():
    """
    Returns a list of dictionaries containing information about the name, address,
    rating, phone number and image of nearby banks.
    """
    post = user.query.all()
    last_post = post[-1]
    place = last_post.location
    lat, lng = find_lat_lng(place)
    radius = 1000
    restaurants_json = gmaps.places_nearby(
        location=[lat, lng], type="bank", radius=radius)

    while not restaurants_json['results']:
        radius += 500
        restaurants_json = gmaps.places_nearby(
            location=[lat, lng], type="bank", radius=radius)

    results = restaurants_json['results']

    photo_references = []
    for i in range(len(results)):
        photos_list = results[i]['photos'] if 'photos' in results[i] else None
        if photos_list:
            photos_dict = photos_list[0]
            photo_references.append(photos_dict['photo_reference'])
        else:
            photo_references.append(None)

    places_id = [d.get('place_id') for d in results]

    info = extract_information(places_id)
    images = get_image_urls(photo_references)

    for i in range(len(info)):
        info[i]["image"] = images[i]

    return render_template('banks.html',info=info)

@app.route('/railway-stations')
def find_bus_stations():
    """
    Returns a list of dictionaries containing information about the name, address,
    rating, phone number and image of nearby bus stations.
    """
    post = user.query.all()
    last_post = post[-1]
    place = last_post.location
    lat, lng = find_lat_lng(place)
    radius = 1000
    restaurants_json = gmaps.places_nearby(
        location=[lat, lng], type="bus_station", radius=radius)

    while not restaurants_json['results']:
        radius += 500
        restaurants_json = gmaps.places_nearby(
            location=[lat, lng], type="bus_station", radius=radius)

    results = restaurants_json['results']

    photo_references = []
    for i in range(len(results)):
        photos_list = results[i]['photos'] if 'photos' in results[i] else None
        if photos_list:
            photos_dict = photos_list[0]
            photo_references.append(photos_dict['photo_reference'])
        else:
            photo_references.append(None)

    places_id = [d.get('place_id') for d in results]

    info = extract_information(places_id)
    images = get_image_urls(photo_references)

    for i in range(len(info)):
        info[i]["image"] = images[i]

    return render_template('metro-stations.html',info=info)

@app.route('/gas-stations')
def find_gas_stations():
    """
    Returns a list of dictionaries containing information about the name, address,
    rating, phone number and image of nearby gas stations.
    """
    post = user.query.all()
    last_post = post[-1]
    place = last_post.location
    lat, lng = find_lat_lng(place)
    radius = 1000
    restaurants_json = gmaps.places_nearby(
        location=[lat, lng], type="gas_station", radius=radius)

    while not restaurants_json['results']:
        radius += 500
        restaurants_json = gmaps.places_nearby(
            location=[lat, lng], type="gas_station", radius=radius)

    results = restaurants_json['results']

    photo_references = []
    for i in range(len(results)):
        photos_list = results[i]['photos'] if 'photos' in results[i] else None
        if photos_list:
            photos_dict = photos_list[0]
            photo_references.append(photos_dict['photo_reference'])
        else:
            photo_references.append(None)

    places_id = [d.get('place_id') for d in results]

    info = extract_information(places_id)
    images = get_image_urls(photo_references)

    for i in range(len(info)):
        info[i]["image"] = images[i]

    return render_template('gas-stations.html',info=info)

@app.route('/doctors')
def find_doctors():
    """
    Returns a list of dictionaries containing information about the name, address,
    rating, phone number and image of nearby doctors.
    """
    post = user.query.all()
    last_post = post[-1]
    place = last_post.location
    lat, lng = find_lat_lng(place)
    radius = 1000
    restaurants_json = gmaps.places_nearby(
        location=[lat, lng], type="doctor", radius=radius)

    while not restaurants_json['results']:
        radius += 500
        restaurants_json = gmaps.places_nearby(
            location=[lat, lng], type="doctor", radius=radius)

    results = restaurants_json['results']

    photo_references = []
    for i in range(len(results)):
        photos_list = results[i]['photos'] if 'photos' in results[i] else None
        if photos_list:
            photos_dict = photos_list[0]
            photo_references.append(photos_dict['photo_reference'])
        else:
            photo_references.append(None)

    places_id = [d.get('place_id') for d in results]

    info = extract_information(places_id)
    images = get_image_urls(photo_references)

    for i in range(len(info)):
        info[i]["image"] = images[i]

    return render_template('doctors.html',info=info)


def get_directions(origin: str, dest: str):
    parameters_directions = {
        'origin': origin,
        'destination': dest,
        'dir_action': 'navigate',
    }
    encoded_maps_url = urlencode(parameters_directions)
    combined_url = f'https://www.google.com/maps/dir/?api=1&{encoded_maps_url}'

    return combined_url

def find_lat_lng(location: str) -> tuple[float, float]:
    """
    Returns the latitude and longtitude of the given location.
    Location can be an address, a station, a city, or even a country
    but country isn't preferred.
    """
    
    g = geocoder.mapbox(location, key='pk.eyJ1IjoicmFodWxzaGFoeiIsImEiOiJja3lpbGdnN2ExNWw0MnZwMDhzdTZxa2FwIn0.po1o8LBd0wnNBE6dpr5Ouw')
    j=g.json
    lat=j["lat"]
    lng=j["lng"]

    return lat, lng

def get_image_urls(photo_references: list) -> list:
    url = "https://maps.googleapis.com/maps/api/place/photo"
    image_urls = []

    for photo_ref in photo_references:
        params = {
            "photo_reference": photo_ref,
            "key": API_KEY,
            "maxwidth": 600,
            "maxheight": 600
        }
        encoded_params = urlencode(params)
        encoded_url = f"{url}?{encoded_params}"
        image_urls.append(encoded_url)

    return image_urls


def extract_information(places_id: tuple) -> list:
    """
    Returns a list of dictionaries containing information about name, address,
    rating and phone number
    """
    info = []
    url_detail_endpoint = "https://maps.googleapis.com/maps/api/place/details/json"

    for place_id in places_id:
        params_detail = {
            'place_id': place_id,
            'fields': 'formatted_address,business_status,name,type,rating,formatted_phone_number,international_phone_number',
            'key': API_KEY}

        encoded_detail_params = urlencode(params_detail)
        encoded_url_detail = f"{url_detail_endpoint}?{encoded_detail_params}"

        r = requests.get(encoded_url_detail).json()
        res = r['result']
        info_dict = {"name": res.get('name'), "rating": res.get('rating'),
                     "address": res.get('formatted_address'),
                     "phone number": res.get('formatted_phone_number')}
        info.append(info_dict)

    return info


def extract_photo_references(places_id: list) -> list:
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    photo_references = []

    for place_id in places_id:
        params = {
            'place_id': place_id,
            'fields': 'photo',
            'key': API_KEY
        }

        encoded_params = urlencode(params)
        encoded_url = f"{url}?{encoded_params}"

        r = requests.get(encoded_url).json()
        res = r['result']
        photos = res['photos'][0] if 'photos' in res else None
        if photos:
            photo_references.append(
                photos['photo_reference']) if 'photo_reference' in photos else None

    return photo_references

if __name__ == "__main__":
    app.run()
