from flask import Blueprint, Flask, render_template, request, jsonify, session
from geopy.geocoders import Nominatim
import swisseph as swe
import datetime
import sqlite3
import hashlib
import json
import os
import pandas as pd
import requests

swe.set_ephe_path('.') 
 

# Custom logic modules
from logic.birth_form_logic import city_df, deg_str_to_decimal, zodiac_signs
from logic.astronihar_api_calc import get_astro_data
from logic.divisionalLogic import (get_absolute_degree,
    get_d1_chart, get_d6_chart,
    get_d9_chart, get_d30_chart, get_d60_chart
)
from logic.divisionalLogic import get_d3_chart_from_d1


main_routes = Blueprint('main_routes', __name__)






@main_routes.route('/')
def index():
    return render_template('birth_form.html')


@main_routes.route('/submit', methods=['POST'])
def submit():
    try:
        name = request.form.get('name')
        date_str = request.form.get('birthdate')
        hour = int(request.form.get('hour'))
        minute = int(request.form.get('minute'))
        ampm = request.form.get('ampm')
        state = request.form.get('state')
        city = request.form.get('city')

        session['birth_datetime'] = date_str
        hour_24 = (hour % 12) + (12 if ampm == 'PM' else 0)
        time_str = f"{hour_24}:{minute:02d}"
        session['timestr'] = time_str

        place = f"{city}, {state}"

        # Get coordinates from city_df or geocode
        city_row = city_df[
            (city_df['state'].str.lower() == state.lower()) & 
            (city_df['city'].str.lower() == city.lower())
        ]
        if not city_row.empty:
            lat = float(city_row.iloc[0]['latitude'])
            lon = float(city_row.iloc[0]['longitude'])
        else:
            geolocator = Nominatim(user_agent="astro_locator")
            location = geolocator.geocode(place)
            if not location:
                return render_template('birth_form.html', error="Invalid place entered.")
            lat, lon = location.latitude, location.longitude

        # Core astro logic
        data = get_astro_data(date_str, time_str, lat, lon)

        dt_obj = datetime.datetime.strptime(f"{date_str} {time_str}", "%d-%m-%Y %H:%M")
        weekday_map = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        weekday = weekday_map[dt_obj.weekday()]

        moon_deg = (zodiac_signs.index(data['planets']['Moon']['zodiac']) * 30) + deg_str_to_decimal(data['planets']['Moon']['degree'])
        sun_deg = (zodiac_signs.index(data['planets']['Sun']['zodiac']) * 30) + deg_str_to_decimal(data['planets']['Sun']['degree'])
        session['moon_degree'] = moon_deg

        tithi_num = int(((moon_deg - sun_deg) % 360) / 12) + 1
        tithi_names = ["Pratipada", "Dvitiya", "Tritiya", "Chaturthi", "Panchami", "Shashti",
                       "Saptami", "Ashtami", "Navami", "Dashami", "Ekadashi", "Dwadashi",
                       "Trayodashi", "Chaturdashi", "Purnima/Amavasya"]
        tithi_phase = tithi_names[(tithi_num - 1) % 15]

        nak = data['planets']['Moon']['nakshatra']
        yoga_names = ["Vishkambha", "Priti", "Ayushman", "Saubhagya", "Shobhana", "Atiganda",
                      "Sukarman", "Dhriti", "Shoola", "Ganda", "Vriddhi", "Dhruva", "Vyaghata",
                      "Harshana", "Vajra", "Siddhi", "Vyatipata", "Variyan", "Parigha", "Shiva",
                      "Siddha", "Sadhya", "Shubha", "Shukla", "Brahma", "Indra", "Vaidhriti"]
        yoga_num = int(((sun_deg + moon_deg) % 360) / (360 / 27))
        yoga = yoga_names[yoga_num]

        karana_names = ["Bava", "Balava", "Kaulava", "Taitila", "Garaja", "Vanija", "Vishti",
                        "Shakuni", "Chatushpada", "Naga", "Kimstughna"]
        karana = karana_names[(2 * (tithi_num - 1)) % len(karana_names)]

        hora_sequence = ["Sun", "Venus", "Mercury", "Moon", "Saturn", "Jupiter", "Mars"]
        hora_lord = hora_sequence[dt_obj.hour % 7]

        left_table = {
            "Date:": dt_obj.strftime("%B %d, %Y"),
            "Time:": dt_obj.strftime("%I:%M %p"),
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

        session['moon_zodiac'] = data['planets']['Moon']['zodiac']

        right_table = {f"Right {i}": f"Info {i}" for i in range(1, 15)}

        # Store everything in session
        session['astro_data'] = json.dumps(data)
        session['left_table'] = json.dumps(left_table)
        session['right_table'] = json.dumps(right_table)
        session['name'] = name

        session['dump_this_in_charts'] = data

        # DB saving
        planet_hash = hashlib.md5(json.dumps(data['planets'], sort_keys=True).encode()).hexdigest()
        conn = sqlite3.connect("astro_data.db")
        c = conn.cursor()
        c.execute("SELECT id FROM planet_positions WHERE data_hash = ?", (planet_hash,))
        row = c.fetchone()
        if row:
            planet_data_id = row[0]
        else:
            c.execute("INSERT INTO planet_positions (data_hash, ascendant, planets) VALUES (?, ?, ?)",
                      (planet_hash, json.dumps(data['ascendant']), json.dumps(data['planets'])))
            planet_data_id = c.lastrowid

        c.execute("SELECT id FROM users WHERE name=? AND birthdate=? AND planet_data_id=?",
                  (name, date_str, planet_data_id))
        if not c.fetchone():
            c.execute("INSERT INTO users (name, birthdate, birthtime, state, city, planet_data_id) VALUES (?, ?, ?, ?, ?, ?)",
                      (name, date_str, time_str, state, city, planet_data_id))
        conn.commit()
        conn.close()


       

        return render_template('result.html', data=data, name=name,
                               left_table=left_table, right_table=right_table)
    except Exception as e:
        return render_template('birth_form.html', error=str(e))