from flask import Flask, render_template, request, jsonify
from geopy.geocoders import Nominatim
import swisseph as swe
import datetime
import sqlite3
import hashlib
import json
import pandas as pd
import re
import os

from logic.birth_form_logic import *
from logic.astronihar_api_calc import *
from logic.divisional import *
from flask import Flask, render_template, request, session



app = Flask(__name__)
swe.set_ephe_path('.')


app.secret_key = os.urandom(24)  




@app.route('/')
def index():
    return render_template('birth_form.html')


# @app.route('/submit', methods=['POST'])
# def submit():
#     name = request.form.get('name')
#     date_str = request.form.get('birthdate')
#     hour = request.form.get('hour')
#     minute = request.form.get('minute')
#     ampm = request.form.get('ampm')
#     state = request.form.get('state')
#     city = request.form.get('city')

#     time_str = f"{int(hour) % 12 + (12 if ampm == 'PM' else 0)}:{minute}"
#     place = f"{city}, {state}"

#     city_state_row = city_df[(city_df['state'].str.lower() == state.lower()) & (city_df['city'].str.lower() == city.lower())]
#     if not city_state_row.empty:
#         lat = float(city_state_row.iloc[0]['latitude'])
#         lon = float(city_state_row.iloc[0]['longitude'])
#     else:
#         geolocator = Nominatim(user_agent="astro_locator")
#         location = geolocator.geocode(place)
#         if not location:
#             return render_template('birth_form.html', error="Invalid place entered.")
#             lat = location.latitude
#             lon = location.longitude

#     # ✅ Store everything in session
#     session['name'] = name
#     session['birthdate'] = date_str
#     session['timestr'] = time_str
#     session['hour'] = hour
#     session['minute'] = minute
#     session['ampm'] = ampm
#     session['state'] = state
#     session['city'] = city
#     session['lat'] = lat
#     session['lon'] = lon




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

        session['birth_datetime'] = date_str
      


        time_str = f"{int(hour) % 12 + (12 if ampm == 'PM' else 0)}:{minute}"
        place = f"{city}, {state}"
        session['timestr'] = time_str

        city_state_row = city_df[(city_df['state'].str.lower() == state.lower()) & (city_df['city'].str.lower() == city.lower())]
        if not city_state_row.empty:
            lat = float(city_state_row.iloc[0]['latitude'])
            lon = float(city_state_row.iloc[0]['longitude'])
        else:
            geolocator = Nominatim(user_agent="astro_locator")
            location = geolocator.geocode(place)
            if not location:
                return render_template('birth_form.html', error="Invalid place entered.")
            lat = location.latitude
            lon = location.longitude



        data = get_astro_data(date_str, time_str, lat, lon)

        weekday_map = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        weekday = weekday_map[datetime.datetime.strptime(f"{date_str} {time_str}", "%d-%m-%Y %H:%M").weekday()]

        moon_total_deg = (zodiac_signs.index(data['planets']['Moon']['zodiac']) * 30) + deg_str_to_decimal(data['planets']['Moon']['degree'])
        session['moon_degree'] = moon_total_deg
        sun_total_deg = (zodiac_signs.index(data['planets']['Sun']['zodiac']) * 30) + deg_str_to_decimal(data['planets']['Sun']['degree'])

        tithi_num = int(((moon_total_deg - sun_total_deg) % 360) / 12) + 1
        tithi_names = ["Pratipada", "Dvitiya", "Tritiya", "Chaturthi", "Panchami", "Shashti",
                        "Saptami", "Ashtami", "Navami", "Dashami", "Ekadashi", "Dwadashi",
                        "Trayodashi", "Chaturdashi", "Purnima/Amavasya"]
        tithi_phase = tithi_names[(tithi_num - 1) % 15]

        nak = data['planets']['Moon']['nakshatra']
        yoga_num = int(((sun_total_deg + moon_total_deg) % 360) / (360 / 27))
        yoga_names = ["Vishkambha", "Priti", "Ayushman", "Saubhagya", "Shobhana", "Atiganda",
                       "Sukarman", "Dhriti", "Shoola", "Ganda", "Vriddhi", "Dhruva", "Vyaghata",
                       "Harshana", "Vajra", "Siddhi", "Vyatipata", "Variyan", "Parigha", "Shiva",
                       "Siddha", "Sadhya", "Shubha", "Shukla", "Brahma", "Indra", "Vaidhriti"]
        yoga = yoga_names[yoga_num]

        karana_names = ["Bava", "Balava", "Kaulava", "Taitila", "Garaja", "Vanija", "Vishti",
                         "Shakuni", "Chatushpada", "Naga", "Kimstughna"]
        karana = karana_names[(2 * (tithi_num - 1)) % len(karana_names)]

        hora_sequence = ["Sun", "Venus", "Mercury", "Moon", "Saturn", "Jupiter", "Mars"]
        hora_index = datetime.datetime.strptime(f"{date_str} {time_str}", "%d-%m-%Y %H:%M").hour % 7
        hora_lord = hora_sequence[hora_index]

        left_table = {
            "Date:": datetime.datetime.strptime(date_str, "%d-%m-%Y").strftime("%B %d, %Y"),
            "Time:": datetime.datetime.strptime(time_str, "%H:%M").strftime("%I:%M %p"),
            "Weekday:": weekday,
            "Tithi:": f"{tithi_phase} ({tithi_num})",
            "Nakshatra:": nak,
            "Yoga:": yoga,
            "Karana:": karana,
            "Hora Lord:": hora_lord,
            "Ascendant:": f"{data['ascendant']['zodiac']} ({data['ascendant']['degree']})",
            "Asc Nakshatra:": f"{data['ascendant']['nakshatra']} (Pada {data['ascendant']['pada']})",
            "Moon Sign:": f"{data['planets']['Moon']['zodiac']} ({data['planets']['Moon']['degree']})",
            "Sun Sign:": f"{data['planets']['Sun']['zodiac']} ({data['planets']['Sun']['degree']})",
            "Karaka:": ', '.join([f"{k}: {v}" for k, v in data['karakas'].items()])
        }

        right_table = {f"Right {i}": f"Info {i}" for i in range(1, 15)}


        session['astro_data'] = json.dumps(data)  
        session['left_table'] = json.dumps(left_table)
        session['right_table'] = json.dumps(right_table)
        session['name'] = name


        ########Removing redundency
        planet_hash = hashlib.md5(json.dumps(data['planets'], sort_keys=True).encode()).hexdigest()
        conn = sqlite3.connect("astro_data.db")
        c = conn.cursor()
        c.execute("SELECT id FROM planet_positions WHERE data_hash = ?", (planet_hash,))
        row = c.fetchone()
        if row:
            planet_data_id = row[0]
        else:
            c.execute("INSERT INTO planet_positions (data_hash, ascendant, planets) VALUES (?, ?, ?)", (
                planet_hash, json.dumps(data['ascendant']), json.dumps(data['planets'])
            ))
            planet_data_id = c.lastrowid

        c.execute("SELECT id FROM users WHERE name=? AND birthdate=? AND planet_data_id=?",
                  (name, date_str, planet_data_id))
        if not c.fetchone():
            c.execute("INSERT INTO users (name, birthdate, birthtime, state, city, planet_data_id) VALUES (?, ?, ?, ?, ?, ?)",
                      (name, date_str, time_str, state, city, planet_data_id))

        conn.commit()
        conn.close()
        #######################Database part
        

        return render_template('result.html', data=data, name=name, left_table=left_table, right_table=right_table)

    except Exception as e:
        return render_template('birth_form.html', error=str(e))

@app.route("/api/states")
def api_states():
    query = request.args.get("query", "").lower()
    states = city_df['state'].dropna().unique()
    suggestions = [s for s in states if query in s.lower()]
    return jsonify({"suggestions": suggestions})

@app.route("/api/cities")
def api_cities():
    state = request.args.get("state", "")
    query = request.args.get("query", "").lower()
    cities = city_df[city_df['state'].str.lower() == state.lower()]['city'].dropna().unique()
    suggestions = [c for c in cities if query in c.lower()]
    return jsonify({"suggestions": suggestions})






@app.route('/home')
def home():
    if 'astro_data' in session:
        data = json.loads(session['astro_data'])
        left_table = json.loads(session['left_table'])
        right_table = json.loads(session['right_table'])
        name = session.get('name', 'Anonymous')
        return render_template('result.html', data=data, name=name, left_table=left_table, right_table=right_table)
    else:
        return "Please submit your birth details first.", 400
    


@app.route('/anatomy')
def anatomy():
    if 'astro_data' in session:
        data = json.loads(session['astro_data'])  # Convert back to dict
        left_table = json.loads(session['left_table'])
        right_table = json.loads(session['right_table'])
        name = session.get('name', 'Anonymous')
        return render_template('anatomy.html', data=data, name=name, left_table=left_table, right_table=right_table)
    else:
        return "No data found in session. Please submit your birth details first.", 400


@app.route('/chakras')
def chakras():
    return render_template('chakras.html')

@app.route('/dasha')
def dasha():
    from logic.dashalogic import get_full_dasha_from_session
    data = get_full_dasha_from_session()
    return render_template('dasha.html', dasha_data=data)



@app.route('/strength')
def strength():
    return render_template('strength.html')

@app.route('/transit')
def transit():
    return render_template('transit.html')

if __name__ == '__main__':
    app.run(debug=True)

