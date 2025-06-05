from flask import Flask, render_template, request, jsonify
from geopy.geocoders import Nominatim
import swisseph as swe
import datetime

app = Flask(__name__)
swe.set_ephe_path('.')  # Set ephemeris path

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
        swe.SUN: 'Sun',
        swe.MOON: 'Moon',
        swe.MERCURY: 'Mercury',
        swe.VENUS: 'Venus',
        swe.MARS: 'Mars',
        swe.JUPITER: 'Jupiter',
        swe.SATURN: 'Saturn',
        swe.MEAN_NODE: 'Rahu'
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
#         'degree': round(asc_deg % 30, 5),
#         'nakshatra': nakshatras[asc_nak],
#         'pada': asc_pada
#     }

#     planets = {
#         swe.SUN: 'Sun',
#         swe.MOON: 'Moon',
#         swe.MERCURY: 'Mercury',
#         swe.VENUS: 'Venus',
#         swe.MARS: 'Mars',
#         swe.JUPITER: 'Jupiter',
#         swe.SATURN: 'Saturn',
#         swe.MEAN_NODE: 'Rahu'
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
#             'degree': round(deg % 30, 5),
#             'nakshatra': nakshatras[nak],
#             'pada': pada
#         }

#         if name == 'Rahu':
#             rahu_deg = deg

#     # Ketu
#     ketu_deg = (rahu_deg + 180) % 360
#     ketu_zodiac = int(ketu_deg / 30)
#     ketu_nak = int(ketu_deg / (360 / 27))
#     ketu_pada = int(((ketu_deg % (360 / 27)) / (13.3333 / 4))) + 1

#     planet_data['Ketu'] = {
#         'zodiac': zodiac_signs[ketu_zodiac],
#         'degree': round(ketu_deg % 30, 5),
#         'nakshatra': nakshatras[ketu_nak],
#         'pada': ketu_pada
#     }

#     return {
#         'timestamp_ist': dt.strftime("%Y-%m-%d %H:%M"),
#         'ascendant': asc_data,
#         'planets': planet_data
#     }

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            date_str = request.form.get('date')       # e.g. 29-12-2005
            time_str = request.form.get('time')       # e.g. 03:21 (24hr format)
            place = request.form.get('place')         # e.g. Ludhiana

            geolocator = Nominatim(user_agent="astro_locator")
            location = geolocator.geocode(f"{place}, India")

            if not location:
                return render_template('index.html', error="Invalid place entered.")

            lat = location.latitude
            lon = location.longitude

            data = get_astro_data(date_str, time_str, lat, lon)
            return jsonify(data)

        except Exception as e:
            return render_template('index.html', error=str(e))

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
