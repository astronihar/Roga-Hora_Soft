from flask import Flask, jsonify
import swisseph as swe
import datetime

app = Flask(__name__)
swe.set_ephe_path('.') 


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

def get_current_astro_data():
    latitude = 28.6139  # Delhi
    longitude = 77.2090


    ist_now = datetime.datetime.now()

  
    utc_now = ist_now - datetime.timedelta(hours=5, minutes=30)

   
    swe.set_sid_mode(swe.SIDM_LAHIRI)

  
    jd = swe.julday(
        utc_now.year, utc_now.month, utc_now.day,
        utc_now.hour + utc_now.minute / 60 + utc_now.second / 3600
    )

    
    cusps, ascmc = swe.houses_ex(jd, latitude, longitude, b'A', swe.FLG_SIDEREAL)
    asc_deg = ascmc[swe.ASC]
    asc_zodiac = int(asc_deg / 30)
    asc_nak = int(asc_deg / (360 / 27))
    asc_pada = int(((asc_deg % (360 / 27)) / (13.3333 / 4))) + 1

    asc_data = {
        'zodiac': zodiac_signs[asc_zodiac],
        'degree': round(asc_deg % 30, 5),
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
            'degree': round(deg % 30, 5),
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
        'degree': round(ketu_deg % 30, 5),
        'nakshatra': nakshatras[ketu_nak],
        'pada': ketu_pada
    }

    return {
        'timestamp_ist': ist_now.strftime("%Y-%m-%d %H:%M:%S"),
        'ascendant': asc_data,
        'planets': planet_data
    }

@app.route('/api/astronihar/d1', methods=['GET'])
def get_astro():
    return jsonify(get_current_astro_data())

if __name__ == '__main__':
    app.run(debug=True, port=5001)