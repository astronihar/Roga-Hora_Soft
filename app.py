from flask import Flask, render_template, request, jsonify, session
from geopy.geocoders import Nominatim
import swisseph as swe
import datetime
import sqlite3
import hashlib
import json
import os
import pandas as pd
import requests

# Custom logic modules
from logic.birth_form_logic import city_df, deg_str_to_decimal, zodiac_signs
from logic.astronihar_api_calc import get_astro_data
from logic.divisionalLogic import (get_absolute_degree,
    get_d1_chart, get_d6_chart,
    get_d9_chart, get_d30_chart, get_d60_chart
)
from logic.divisionalLogic import get_d3_chart_from_d1


app = Flask(__name__)
app.secret_key = os.urandom(24)  
swe.set_ephe_path('.')  


ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

def zodiac_index(zodiac_name):
    try:
        return ZODIAC_SIGNS.index(zodiac_name)
    except ValueError:
        raise Exception(f"Invalid zodiac sign: {zodiac_name}")

def prepare_planets_raw(planets_data):
    result = {}
    for planet, val in planets_data.items():
        sign_index = zodiac_index(val['zodiac'])
        degree = val['degree']
        result[planet] = get_absolute_degree(sign_index, degree)
    return result



@app.route('/')
def index():
    return render_template('birth_form.html')


@app.route('/submit', methods=['POST'])
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


       

        return render_template('result.html', data=data, name=name,divisionals=data['divisionals'],
                               left_table=left_table, right_table=right_table)
    except Exception as e:
        return render_template('birth_form.html', error=str(e))

@app.route('/home')
def home():
    if 'astro_data' in session:
        data = json.loads(session['astro_data'])
        left_table = json.loads(session['left_table'])
        right_table = json.loads(session['right_table'])
        name = session.get('name', 'Anonymous')
        return render_template('result.html', data=data, name=name, left_table=left_table, right_table=right_table,divisionals=data.get('divisionals', {}))
    return "Please submit your birth details first.", 400

@app.route('/anatomy')
def anatomy():
    if 'astro_data' in session:
        data = json.loads(session['astro_data'])
        left_table = json.loads(session['left_table'])
        right_table = json.loads(session['right_table'])
        name = session.get('name', 'Anonymous')
        return render_template('anatomy.html', data=data, name=name, left_table=left_table, right_table=right_table)
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



@app.route('/api/states')
def api_states():
    query = request.args.get("query", "").lower()
    states = city_df['state'].dropna().unique()
    suggestions = [s for s in states if query in s.lower()]
    return jsonify({"suggestions": suggestions})

@app.route('/api/cities')
def api_cities():
    state = request.args.get("state", "")
    query = request.args.get("query", "").lower()
    cities = city_df[city_df['state'].str.lower() == state.lower()]['city'].dropna().unique()
    suggestions = [c for c in cities if query in c.lower()]
    return jsonify({"suggestions": suggestions})


zodiac_list = [
    'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
    'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
]



@app.route('/transit')
def transit():
    try:
        response = requests.get('http://127.0.0.1:5001/api/astronihar/d1')
        data = response.json()
    except Exception as e:
        return f"Error fetching planetary data: {e}"

    zodiac_list = [
        'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
        'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
    ]

    ### ------------------ Chart 1: Live Ascendant ------------------ ###
    asc_zodiac = data['ascendant']['zodiac']
    asc_index = zodiac_list.index(asc_zodiac)
    rotated_zodiacs = zodiac_list[asc_index:] + zodiac_list[:asc_index]
    rotated_zodiac_numbers = [(zodiac_list.index(z) + 1) for z in rotated_zodiacs]

    chart_live = {}
    for i in range(1, 13):
        chart_live[i] = {
            'zodiac': rotated_zodiac_numbers[i - 1],
            'planets': []
        }
    chart_live[1]['planets'].append("Ascendant")

    for planet, info in data['planets'].items():
        try:
            planet_zodiac = info['zodiac']
            degree = round(info['degree'], 5)
            planet_zod_index = zodiac_list.index(planet_zodiac)
            house_pos = (planet_zod_index - asc_index) % 12 + 1
            zodiac_number = planet_zod_index + 1
            chart_live[house_pos]['planets'].append(f"{planet}^{degree} ({zodiac_number})")
        except:
            continue

    ### ------------------ Chart 2: Fixed Ascendant = Moon Sign ------------------ ###
    moon_zodiac = session.get('moon_zodiac', asc_zodiac)  # fallback to live if not present
    moon_index = zodiac_list.index(moon_zodiac)
    rotated_zodiacs_fixed = zodiac_list[moon_index:] + zodiac_list[:moon_index]
    rotated_zodiac_numbers_fixed = [(zodiac_list.index(z) + 1) for z in rotated_zodiacs_fixed]

    chart_moon = {}
    for i in range(1, 13):
        chart_moon[i] = {
            'zodiac': rotated_zodiac_numbers_fixed[i - 1],
            'planets': []
        }
    chart_moon[1]['planets'].append("Ascendant")  # fixed to Moon sign

    for planet, info in data['planets'].items():
        try:
            planet_zodiac = info['zodiac']
            degree = round(info['degree'], 5)
            planet_zod_index = zodiac_list.index(planet_zodiac)
            house_pos = (planet_zod_index - moon_index) % 12 + 1
            zodiac_number = planet_zod_index + 1
            chart_moon[house_pos]['planets'].append(f"{planet}^{degree} ({zodiac_number})")
        except:
            continue

    return render_template(
        # 'transit.html',
        # divisionals={'D1': chart_live},
        # fixed_chart={'D1': chart_moon}
        'transit.html',
        divisionals={'D1': chart_live},
        fixed_chart={'D1': chart_moon},
        planet_table=data['planets'],
        ascendant=data['ascendant'],
        data=data
    )


@app.route('/charts')
def show_charts():
    url = "http://127.0.0.1:5001/api/astronihar/d1"
    try:
        res = requests.get(url)
        data = res.json()
    except Exception as e:
        return f"⚠️ Error fetching API data: {e}"

    asc_data = data.get('ascendant', {})
    asc_sign_index = zodiac_index(asc_data.get('zodiac', ''))
    asc_deg = get_absolute_degree(asc_sign_index, asc_data.get('degree', 0))

    planets_raw = prepare_planets_raw(data.get('planets', {}))

    # ✅✅✅ STORE D1 FOR REUSE
    session['asc_deg'] = asc_deg
    session['planets_raw'] = planets_raw

    d1 = get_d1_chart(planets_raw, asc_deg)
    # ✅✅✅ USE CUSTOM D3 LOGIC IMPORTED FROM dashaLogic.py
    d3 = get_d3_chart_from_d1(planets_raw, asc_deg)
    d6 = get_d6_chart(planets_raw, asc_deg)
    d9 = get_d9_chart(planets_raw, asc_deg)
    d30 = get_d30_chart(planets_raw, asc_deg)
    d60 = get_d60_chart(planets_raw, asc_deg)

    return render_template(
        'partials/horoscope_charts.html',
        d1=d1, d3=d3, d6=d6, d9=d9, d30=d30, d60=d60
    )




if __name__ == '__main__':
    app.run(debug=True, port=5000)
