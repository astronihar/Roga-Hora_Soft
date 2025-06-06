# # from flask import Flask, render_template, request, jsonify
# # from geopy.geocoders import Nominatim
# # import swisseph as swe
# # import datetime
# # import sqlite3
# # import hashlib
# # import json

# # app = Flask(__name__)
# # swe.set_ephe_path('.')  # Set ephemeris path

# # # Zodiac and Nakshatra names
# # zodiac_signs = [
# #     'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
# #     'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
# # ]

# # nakshatras = [
# #     "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashirsha", "Ardra", "Punarvasu",
# #     "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta",
# #     "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha",
# #     "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada",
# #     "Uttara Bhadrapada", "Revati"
# # ]

# # # Convert decimal degrees to degrees, minutes, seconds
# # def decimal_to_dms(degree):
# #     d = int(degree)
# #     m = int((degree - d) * 60)
# #     s = round(((degree - d) * 60 - m) * 60)
# #     return f"{d}°{m}′{s}″"

# # # Core Astro Logic
# # def get_astro_data(date_str, time_str, latitude, longitude):
# #     dt = datetime.datetime.strptime(f"{date_str} {time_str}", "%d-%m-%Y %H:%M")
# #     utc_dt = dt - datetime.timedelta(hours=5, minutes=30)

# #     swe.set_sid_mode(swe.SIDM_LAHIRI)
# #     jd = swe.julday(
# #         utc_dt.year, utc_dt.month, utc_dt.day,
# #         utc_dt.hour + utc_dt.minute / 60 + utc_dt.second / 3600
# #     )

# #     cusps, ascmc = swe.houses_ex(jd, latitude, longitude, b'A', swe.FLG_SIDEREAL)
# #     asc_deg = ascmc[swe.ASC]
# #     asc_zodiac = int(asc_deg / 30)
# #     asc_nak = int(asc_deg / (360 / 27))
# #     asc_pada = int(((asc_deg % (360 / 27)) / (13.3333 / 4))) + 1

# #     asc_data = {
# #         'zodiac': zodiac_signs[asc_zodiac],
# #         'degree': decimal_to_dms(asc_deg % 30),
# #         'nakshatra': nakshatras[asc_nak],
# #         'pada': asc_pada
# #     }

# #     planets = {
# #         swe.SUN: 'Sun',
# #         swe.MOON: 'Moon',
# #         swe.MERCURY: 'Mercury',
# #         swe.VENUS: 'Venus',
# #         swe.MARS: 'Mars',
# #         swe.JUPITER: 'Jupiter',
# #         swe.SATURN: 'Saturn',
# #         swe.MEAN_NODE: 'Rahu'
# #     }

# #     planet_data = {}

# #     for code, name in planets.items():
# #         pos, _ = swe.calc(jd, code, swe.FLG_SIDEREAL)
# #         deg = pos[0]
# #         zodiac = int(deg / 30)
# #         nak = int(deg / (360 / 27))
# #         pada = int(((deg % (360 / 27)) / (13.3333 / 4))) + 1

# #         planet_data[name] = {
# #             'zodiac': zodiac_signs[zodiac],
# #             'degree': decimal_to_dms(deg % 30),
# #             'nakshatra': nakshatras[nak],
# #             'pada': pada
# #         }

# #         if name == 'Rahu':
# #             rahu_deg = deg

# #     ketu_deg = (rahu_deg + 180) % 360
# #     ketu_zodiac = int(ketu_deg / 30)
# #     ketu_nak = int(ketu_deg / (360 / 27))
# #     ketu_pada = int(((ketu_deg % (360 / 27)) / (13.3333 / 4))) + 1

# #     planet_data['Ketu'] = {
# #         'zodiac': zodiac_signs[ketu_zodiac],
# #         'degree': decimal_to_dms(ketu_deg % 30),
# #         'nakshatra': nakshatras[ketu_nak],
# #         'pada': ketu_pada
# #     }

# #     return {
# #         'timestamp_ist': dt.strftime("%Y-%m-%d %H:%M"),
# #         'ascendant': asc_data,
# #         'planets': planet_data
# #     }

# # # Routes
# # @app.route('/')
# # def index():
# #     return render_template('birth_form.html')

# # @app.route('/submit', methods=['POST'])
# # def submit():
# #     try:
# #         name = request.form.get('name')
# #         date_str = request.form.get('birthdate')
# #         hour = request.form.get('hour')
# #         minute = request.form.get('minute')
# #         ampm = request.form.get('ampm')
# #         state = request.form.get('state')
# #         city = request.form.get('city')

# #         time_str = f"{int(hour) % 12 + (12 if ampm == 'PM' else 0)}:{minute}"
# #         place = f"{city}, {state}"

# #         geolocator = Nominatim(user_agent="astro_locator")
# #         location = geolocator.geocode(place)
# #         if not location:
# #             return render_template('birth_form.html', error="Invalid place entered.")

# #         lat = location.latitude
# #         lon = location.longitude
# #         data = get_astro_data(date_str, time_str, lat, lon)

# #         planet_hash = hashlib.md5(json.dumps(data['planets'], sort_keys=True).encode()).hexdigest()

# #         conn = sqlite3.connect("astro_data.db")
# #         c = conn.cursor()

# #         # Check if this planetary data already exists
# #         c.execute("SELECT id FROM planet_positions WHERE data_hash = ?", (planet_hash,))
# #         row = c.fetchone()
# #         if row:
# #             planet_data_id = row[0]
# #         else:
# #             c.execute("INSERT INTO planet_positions (data_hash, ascendant, planets) VALUES (?, ?, ?)", (
# #                 planet_hash,
# #                 json.dumps(data['ascendant']),
# #                 json.dumps(data['planets'])
# #             ))
# #             planet_data_id = c.lastrowid

# #         # Prevent duplicate user insertion
# #         c.execute("SELECT id FROM users WHERE name=? AND birthdate=? AND planet_data_id=?", 
# #                   (name, date_str, planet_data_id))
# #         existing_user = c.fetchone()

# #         if not existing_user:
# #             c.execute("INSERT INTO users (name, birthdate, birthtime, state, city, planet_data_id) VALUES (?, ?, ?, ?, ?, ?)", (
# #                 name, date_str, time_str, state, city, planet_data_id
# #             ))

# #         conn.commit()
# #         conn.close()

# #         return jsonify(data)

# #     except Exception as e:
# #         return render_template('birth_form.html', error=str(e))

# # # API for dynamic state suggestions
# # @app.route("/api/states")
# # def api_states():
# #     states = ["Punjab", "Maharashtra", "Karnataka", "Tamil Nadu"]
# #     query = request.args.get("query", "").lower()
# #     return jsonify({"suggestions": [s for s in states if query in s.lower()]})

# # # API for dynamic city suggestions
# # @app.route("/api/cities")
# # def api_cities():
# #     state = request.args.get("state", "")
# #     query = request.args.get("query", "").lower()
# #     cities_by_state = {
# #         "Punjab": ["Ludhiana", "Amritsar", "Barnala"],
# #         "Maharashtra": ["Mumbai", "Pune"],
# #         "Karnataka": ["Bangalore", "Mysore"],
# #         "Tamil Nadu": ["Chennai", "Coimbatore"]
# #     }
# #     cities = cities_by_state.get(state, [])
# #     return jsonify({"suggestions": [c for c in cities if query in c.lower()]})

# # if __name__ == '__main__':
# #     app.run(debug=True)











# from flask import Flask, render_template, request, jsonify
# from geopy.geocoders import Nominatim
# import swisseph as swe
# import datetime
# import sqlite3
# import hashlib
# import json
# import pandas as pd

# app = Flask(__name__)
# swe.set_ephe_path('.')

# # Load city-state dataset
# city_df = pd.read_csv("cities.csv")  # Must have columns: state, city
# city_df['state'] = city_df['state'].astype(str)
# city_df['city'] = city_df['city'].astype(str)

# # Zodiac and Nakshatra names
# zodiac_signs = [
#     'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
#     'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
# ]

# nakshatras = [
#     "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashirsha", "Ardra", "Punarvasu",
#     "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta",
#     "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha",
#     "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada",
#     "Uttara Bhadrapada", "Revati"
# ]

# def decimal_to_dms(degree):
#     d = int(degree)
#     m = int((degree - d) * 60)
#     s = round(((degree - d) * 60 - m) * 60)
#     return f"{d}°{m}′{s}″"

# def get_astro_data(date_str, time_str, latitude, longitude):
#     dt = datetime.datetime.strptime(f"{date_str} {time_str}", "%d-%m-%Y %H:%M")
#     utc_dt = dt - datetime.timedelta(hours=5, minutes=30)

#     swe.set_sid_mode(swe.SIDM_LAHIRI)
#     jd = swe.julday(
#         utc_dt.year, utc_dt.month, utc_dt.day,
#         utc_dt.hour + utc_dt.minute / 60 + utc_dt.second / 3600
#     )

#     cusps, ascmc = swe.houses_ex(jd, latitude, longitude, b'A', swe.FLG_SIDEREAL)
#     asc_deg = ascmc[swe.ASC]
#     asc_zodiac = int(asc_deg / 30)
#     asc_nak = int(asc_deg / (360 / 27))
#     asc_pada = int(((asc_deg % (360 / 27)) / (13.3333 / 4))) + 1

#     asc_data = {
#         'zodiac': zodiac_signs[asc_zodiac],
#         'degree': decimal_to_dms(asc_deg % 30),
#         'nakshatra': nakshatras[asc_nak],
#         'pada': asc_pada
#     }

#     planets = {
#         swe.SUN: 'Sun', swe.MOON: 'Moon', swe.MERCURY: 'Mercury',
#         swe.VENUS: 'Venus', swe.MARS: 'Mars', swe.JUPITER: 'Jupiter',
#         swe.SATURN: 'Saturn', swe.MEAN_NODE: 'Rahu'
#     }

#     planet_data = {}
#     for code, name in planets.items():
#         pos, _ = swe.calc(jd, code, swe.FLG_SIDEREAL)
#         deg = pos[0]
#         zodiac = int(deg / 30)
#         nak = int(deg / (360 / 27))
#         pada = int(((deg % (360 / 27)) / (13.3333 / 4))) + 1
#         planet_data[name] = {
#             'zodiac': zodiac_signs[zodiac],
#             'degree': decimal_to_dms(deg % 30),
#             'nakshatra': nakshatras[nak],
#             'pada': pada
#         }
#         if name == 'Rahu':
#             rahu_deg = deg

#     ketu_deg = (rahu_deg + 180) % 360
#     ketu_zodiac = int(ketu_deg / 30)
#     ketu_nak = int(ketu_deg / (360 / 27))
#     ketu_pada = int(((ketu_deg % (360 / 27)) / (13.3333 / 4))) + 1

#     planet_data['Ketu'] = {
#         'zodiac': zodiac_signs[ketu_zodiac],
#         'degree': decimal_to_dms(ketu_deg % 30),
#         'nakshatra': nakshatras[ketu_nak],
#         'pada': ketu_pada
#     }

#     return {
#         'timestamp_ist': dt.strftime("%Y-%m-%d %H:%M"),
#         'ascendant': asc_data,
#         'planets': planet_data
#     }

# @app.route('/')
# def index():
#     return render_template('birth_form.html')

# @app.route('/submit', methods=['POST'])
# def submit():
#     try:
#         name = request.form.get('name')
#         date_str = request.form.get('birthdate')
#         hour = request.form.get('hour')
#         minute = request.form.get('minute')
#         ampm = request.form.get('ampm')
#         state = request.form.get('state')
#         city = request.form.get('city')

#         time_str = f"{int(hour) % 12 + (12 if ampm == 'PM' else 0)}:{minute}"
#         place = f"{city}, {state}"

#         geolocator = Nominatim(user_agent="astro_locator")
#         location = geolocator.geocode(place)
#         if not location:
#             return render_template('birth_form.html', error="Invalid place entered.")

#         lat = location.latitude
#         lon = location.longitude
#         data = get_astro_data(date_str, time_str, lat, lon)

#         planet_hash = hashlib.md5(json.dumps(data['planets'], sort_keys=True).encode()).hexdigest()

#         conn = sqlite3.connect("astro_data.db")
#         c = conn.cursor()

#         c.execute("SELECT id FROM planet_positions WHERE data_hash = ?", (planet_hash,))
#         row = c.fetchone()
#         if row:
#             planet_data_id = row[0]
#         else:
#             c.execute("INSERT INTO planet_positions (data_hash, ascendant, planets) VALUES (?, ?, ?)", (
#                 planet_hash,
#                 json.dumps(data['ascendant']),
#                 json.dumps(data['planets'])
#             ))
#             planet_data_id = c.lastrowid

#         c.execute("SELECT id FROM users WHERE name=? AND birthdate=? AND planet_data_id=?",
#                   (name, date_str, planet_data_id))
#         existing_user = c.fetchone()

#         if not existing_user:
#             c.execute("INSERT INTO users (name, birthdate, birthtime, state, city, planet_data_id) VALUES (?, ?, ?, ?, ?, ?)", (
#                 name, date_str, time_str, state, city, planet_data_id
#             ))

#         conn.commit()
#         conn.close()

#         return jsonify(data)

#     except Exception as e:
#         return render_template('birth_form.html', error=str(e))

# # API to get state suggestions
# @app.route("/api/states")
# def api_states():
#     query = request.args.get("query", "").lower()
#     states = city_df['state'].dropna().unique()
#     suggestions = [s for s in states if query in s.lower()]
#     return jsonify({"suggestions": suggestions})

# # API to get city suggestions by state
# @app.route("/api/cities")
# def api_cities():
#     state = request.args.get("state", "")
#     query = request.args.get("query", "").lower()
#     cities = city_df[city_df['state'] == state]['city'].dropna().unique()
#     suggestions = [c for c in cities if query in c.lower()]
#     return jsonify({"suggestions": suggestions})

# if __name__ == '__main__':
#     app.run(debug=True)















from flask import Flask, render_template, request, jsonify
from geopy.geocoders import Nominatim
import swisseph as swe
import datetime
import sqlite3
import hashlib
import json
import pandas as pd
import zipfile
import os

app = Flask(__name__)
swe.set_ephe_path('.')

# # Extract city-state dataset from ZIP file if not already extracted
# def extract_dataset(zip_path, extract_to='.'):
#     if not os.path.exists(extract_to + '/cities.csv'):
#         with zipfile.ZipFile(zip_path, 'r') as zip_ref:
#             zip_ref.extractall(extract_to)

# # Extract dataset
# extract_dataset("cities.zip")  # Adjust path if needed

# Load city-state dataset
city_df = pd.read_csv("Indian_Cities_Geo_Data.csv")  # Dataset must have columns: state, city
city_df['state'] = city_df['state'].astype(str)
city_df['city'] = city_df['city'].astype(str)

# Zodiac and Nakshatra names
zodiac_signs = [
    'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
    'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
]

nakshatras = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashirsha", "Ardra", "Punarvasu",
    "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta",
    "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha",
    "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada",
    "Uttara Bhadrapada", "Revati"
]

def decimal_to_dms(degree):
    d = int(degree)
    m = int((degree - d) * 60)
    s = round(((degree - d) * 60 - m) * 60)
    return f"{d}°{m}′{s}″"

def get_astro_data(date_str, time_str, latitude, longitude):
    dt = datetime.datetime.strptime(f"{date_str} {time_str}", "%d-%m-%Y %H:%M")
    utc_dt = dt - datetime.timedelta(hours=5, minutes=30)

    swe.set_sid_mode(swe.SIDM_LAHIRI)
    jd = swe.julday(
        utc_dt.year, utc_dt.month, utc_dt.day,
        utc_dt.hour + utc_dt.minute / 60 + utc_dt.second / 3600
    )

    cusps, ascmc = swe.houses_ex(jd, latitude, longitude, b'A', swe.FLG_SIDEREAL)
    asc_deg = ascmc[swe.ASC]
    asc_zodiac = int(asc_deg / 30)
    asc_nak = int(asc_deg / (360 / 27))
    asc_pada = int(((asc_deg % (360 / 27)) / (13.3333 / 4))) + 1

    asc_data = {
        'zodiac': zodiac_signs[asc_zodiac],
        'degree': decimal_to_dms(asc_deg % 30),
        'nakshatra': nakshatras[asc_nak],
        'pada': asc_pada
    }

    planets = {
        swe.SUN: 'Sun', swe.MOON: 'Moon', swe.MERCURY: 'Mercury',
        swe.VENUS: 'Venus', swe.MARS: 'Mars', swe.JUPITER: 'Jupiter',
        swe.SATURN: 'Saturn', swe.MEAN_NODE: 'Rahu'
    }

    planet_data = {}
    for code, name in planets.items():
        pos, _ = swe.calc(jd, code, swe.FLG_SIDEREAL)
        deg = pos[0]
        zodiac = int(deg / 30)
        nak = int(deg / (360 / 27))
        pada = int(((deg % (360 / 27)) / (13.3333 / 4))) + 1
        planet_data[name] = {
            'zodiac': zodiac_signs[zodiac],
            'degree': decimal_to_dms(deg % 30),
            'nakshatra': nakshatras[nak],
            'pada': pada
        }
        if name == 'Rahu':
            rahu_deg = deg

    ketu_deg = (rahu_deg + 180) % 360
    ketu_zodiac = int(ketu_deg / 30)
    ketu_nak = int(ketu_deg / (360 / 27))
    ketu_pada = int(((ketu_deg % (360 / 27)) / (13.3333 / 4))) + 1

    planet_data['Ketu'] = {
        'zodiac': zodiac_signs[ketu_zodiac],
        'degree': decimal_to_dms(ketu_deg % 30),
        'nakshatra': nakshatras[ketu_nak],
        'pada': ketu_pada
    }

    return {
        'timestamp_ist': dt.strftime("%Y-%m-%d %H:%M"),
        'ascendant': asc_data,
        'planets': planet_data
    }

@app.route('/')
def index():
    return render_template('birth_form.html')

@app.route('/submit', methods=['POST'])
def submit():
    try:
        name = request.form.get('name')
        date_str = request.form.get('birthdate')
        hour = request.form.get('hour')
        minute = request.form.get('minute')
        ampm = request.form.get('ampm')
        state = request.form.get('state')
        city = request.form.get('city')

        time_str = f"{int(hour) % 12 + (12 if ampm == 'PM' else 0)}:{minute}"
        place = f"{city}, {state}"

        # Try to get latitude and longitude from dataset for city + state if available
        city_state_row = city_df[(city_df['state'].str.lower() == state.lower()) & (city_df['city'].str.lower() == city.lower())]
        if not city_state_row.empty and 'latitude' in city_state_row.columns and 'longitude' in city_state_row.columns:
            lat = float(city_state_row.iloc[0]['latitude'])
            lon = float(city_state_row.iloc[0]['longitude'])
        else:
            # fallback to geopy geocoder
            geolocator = Nominatim(user_agent="astro_locator")
            location = geolocator.geocode(place)
            if not location:
                return render_template('birth_form.html', error="Invalid place entered.")
            lat = location.latitude
            lon = location.longitude

        data = get_astro_data(date_str, time_str, lat, lon)

        planet_hash = hashlib.md5(json.dumps(data['planets'], sort_keys=True).encode()).hexdigest()

        conn = sqlite3.connect("astro_data.db")
        c = conn.cursor()

        # Check if this planetary data already exists
        c.execute("SELECT id FROM planet_positions WHERE data_hash = ?", (planet_hash,))
        row = c.fetchone()
        if row:
            planet_data_id = row[0]
        else:
            c.execute("INSERT INTO planet_positions (data_hash, ascendant, planets) VALUES (?, ?, ?)", (
                planet_hash,
                json.dumps(data['ascendant']),
                json.dumps(data['planets'])
            ))
            planet_data_id = c.lastrowid

        # Prevent duplicate user insertion
        c.execute("SELECT id FROM users WHERE name=? AND birthdate=? AND planet_data_id=?", 
                  (name, date_str, planet_data_id))
        existing_user = c.fetchone()

        if not existing_user:
            c.execute("INSERT INTO users (name, birthdate, birthtime, state, city, planet_data_id) VALUES (?, ?, ?, ?, ?, ?)", (
                name, date_str, time_str, state, city, planet_data_id
            ))

        conn.commit()
        conn.close()

        return jsonify(data)

    except Exception as e:
        return render_template('birth_form.html', error=str(e))

# API to get state suggestions with partial match
@app.route("/api/states")
def api_states():
    query = request.args.get("query", "").lower()
    states = city_df['state'].dropna().unique()
    suggestions = [s for s in states if query in s.lower()]
    return jsonify({"suggestions": suggestions})

# API to get city suggestions by state with partial match
@app.route("/api/cities")
def api_cities():
    state = request.args.get("state", "")
    query = request.args.get("query", "").lower()
    cities = city_df[city_df['state'].str.lower() == state.lower()]['city'].dropna().unique()
    suggestions = [c for c in cities if query in c.lower()]
    return jsonify({"suggestions": suggestions})

if __name__ == '__main__':
    app.run(debug=True)





















