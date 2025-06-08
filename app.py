from flask import Flask, render_template, request, jsonify
from geopy.geocoders import Nominatim
from divisional import get_d3_chart, get_d6_chart, get_d9_chart, get_d30_chart, get_d60_chart
import swisseph as swe
import datetime
import sqlite3
import hashlib
import json
import pandas as pd
import re
# from logic.anatomylogic import extract_anatomy_data


app = Flask(__name__)
swe.set_ephe_path('.')

city_df = pd.read_csv("Indian_Cities_Geo_Data.csv")
city_df['state'] = city_df['state'].astype(str)
city_df['city'] = city_df['city'].astype(str)

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

def dms_to_decimal(dms_str):
    match = re.match(r"(\d+)[°º](\d+)[′'](\d+)[″\"]?", dms_str)
    if match:
        deg, min_, sec = map(int, match.groups())
        return deg + (min_ / 60) + (sec / 3600)
    return 0.0

def deg_str_to_decimal(deg_str):
    match = re.match(r"(\d+)°(\d+)′(\d+)″", deg_str)
    if match:
        d, m, s = map(int, match.groups())
        return d + m / 60 + s / 3600
    return 0.0

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

    absolute_degrees = {name: swe.calc(jd, code, swe.FLG_SIDEREAL)[0][0] for code, name in planets.items()}
    absolute_degrees['Ketu'] = ketu_deg
    asc_absolute_deg = asc_deg

    d3_chart = get_d3_chart(absolute_degrees, asc_absolute_deg)
    d9_chart = get_d9_chart(absolute_degrees, asc_absolute_deg)
    d6_chart = get_d6_chart(absolute_degrees, asc_absolute_deg)
    d30_chart = get_d30_chart(absolute_degrees, asc_absolute_deg)
    d60_chart = get_d60_chart(absolute_degrees, asc_absolute_deg)

    karaka_order = ['AK', 'AmK', 'BK', 'MK', 'PuK', 'GnK', 'DK']
    karaka_candidates = {
        planet: dms_to_decimal(data['degree'])
        for planet, data in planet_data.items()
        if planet not in ['Rahu', 'Ketu']
    }
    sorted_karakas = sorted(karaka_candidates.items(), key=lambda x: x[1], reverse=True)
    karakas = {karaka_order[i]: planet for i, (planet, _) in enumerate(sorted_karakas)}
    for i, (planet, _) in enumerate(sorted_karakas):
        if i < len(karaka_order):
            planet_data[planet]['karaka'] = karaka_order[i]

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



@app.route('/anatomy')
def anatomy():
    # TEMP INPUTS (you can make it dynamic later)
    date_str = "07-06-1995"
    time_str = "15:45"
    lat = 28.6139
    lon = 77.2090

    result = extract_anatomy_data(date_str, time_str, lat, lon)
    return render_template('anatomy.html', data=result)



@app.route('/chakras')
def chakras():
    return render_template('chakras.html')

@app.route('/dasha')
def dasha():
    return render_template('dasha.html')

@app.route('/strength')
def strength():
    return render_template('strength.html')

@app.route('/transit')
def transit():
    return render_template('transit.html')

if __name__ == '__main__':
    app.run(debug=True)

