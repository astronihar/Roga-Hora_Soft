
from flask import Flask, render_template, request, jsonify
from geopy.geocoders import Nominatim
from divisional import get_d3_chart, get_d6_chart, get_d9_chart, get_d30_chart, get_d60_chart
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

    # return {
    #     'timestamp_ist': dt.strftime("%Y-%m-%d %H:%M"),
    #     'ascendant': asc_data,
    #     'planets': planet_data
    # }

     
    # Collect absolute degrees for divisional use
    absolute_degrees = {}
    for code, name in planets.items():
        pos, _ = swe.calc(jd, code, swe.FLG_SIDEREAL)
        absolute_degrees[name] = pos[0]

    absolute_degrees['Ketu'] = ketu_deg
    asc_absolute_deg = ascmc[swe.ASC]

    # Compute divisionals
    d3_chart = get_d3_chart(absolute_degrees, asc_absolute_deg)
    d9_chart = get_d9_chart(absolute_degrees, asc_absolute_deg)
    d6_chart = get_d6_chart(absolute_degrees, asc_absolute_deg)
    d30_chart = get_d30_chart(absolute_degrees, asc_absolute_deg)
    d60_chart = get_d60_chart(absolute_degrees, asc_absolute_deg)

    

    import re

    karaka_order = ['AK', 'AmK', 'BK', 'MK', 'PuK', 'GnK', 'DK']

    def dms_to_decimal(dms_str):
      """Convert DMS like '27°8′60″' to decimal degrees."""
      match = re.match(r"(\d+)[°º](\d+)[′'](\d+)[″\"]?", dms_str)
      if match:
        deg, min_, sec = map(int, match.groups())
        return deg + (min_ / 60) + (sec / 3600)
      else:
         return 0.0

# Only planets considered for karakas
    karaka_candidates = {
    planet: dms_to_decimal(data['degree']) 
    for planet, data in planet_data.items()
    if planet not in ['Rahu', 'Ketu']
}

# Sort by descending total degrees
    sorted_karakas = sorted(karaka_candidates.items(), key=lambda x: x[1], reverse=True)

# Assign karakas to planets
    karakas = {}
    for i, (planet_name, _) in enumerate(sorted_karakas):
      if i < len(karaka_order):
        planet_data[planet_name]['karaka'] = karaka_order[i]
        karakas[karaka_order[i]] = planet_name

    return {
        'timestamp_ist': dt.strftime("%Y-%m-%d %H:%M"),
        'ascendant': asc_data,
        'planets': planet_data,
        'karakas': karakas,  
        'divisionals': {
            'D3': d3_chart,
            'D9': d9_chart,
            'D6': d6_chart,
            'D30': d30_chart,
            'D60': d60_chart
        }
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

        # return jsonify(data) ------------------------------------------------------------- This is where i rendered my html insted of json :)
        return render_template('result.html', data=data, name=name)

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




####################################################
























