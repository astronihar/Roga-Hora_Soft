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

# Custom logic modules
from logic.birth_form_logic import city_df, deg_str_to_decimal, zodiac_signs
from logic.astronihar_api_calc import get_astro_data
from logic.divisionalLogic import (get_absolute_degree,
    get_d1_chart, get_d6_chart,
    get_d9_chart, get_d30_chart, get_d60_chart
)
from logic.divisionalLogic import get_d3_chart_from_d1


charts_routes = Blueprint('charts_routes', __name__)




def zodiac_index(zodiac_name):
    try:
        return ZODIAC_SIGNS.index(zodiac_name)
    except ValueError:
        raise Exception(f"Invalid zodiac sign: {zodiac_name}")


ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]



import re

def dms_to_decimal(dms_str):
    # Safely handle if it's already float-like
    if isinstance(dms_str, (int, float)):
        return float(dms_str)

    # Extract numbers
    match = re.findall(r"(\d+)", dms_str)
    if len(match) == 3:
        deg, mins, secs = map(int, match)
        return deg + mins / 60 + secs / 3600
    elif len(match) == 2:
        deg, mins = map(int, match)
        return deg + mins / 60
    elif len(match) == 1:
        return float(match[0])
    else:
        raise ValueError(f"Invalid DMS format: {dms_str}")
    

    

def prepare_planets_raw(planets_data):
    result = {}
    for planet, pdata in planets_data.items():
        sign_index = zodiac_index(pdata['zodiac'])
        degree = dms_to_decimal(pdata['degree'])  # <== string to float here
        result[planet] = get_absolute_degree(sign_index, degree)
    return result





@charts_routes.route('/chakras')
def show_charts():
    data = session.get('dump_this_in_charts')
    if not data:
        return "⚠️ No data found in session. Please submit birth details first."

    asc_data = data.get('ascendant', {})
    asc_sign_index = zodiac_index(asc_data.get('zodiac', ''))
    
    asc_deg_raw = asc_data.get('degree', '0')
    asc_deg = get_absolute_degree(asc_sign_index, dms_to_decimal(asc_deg_raw))

    planets_raw = prepare_planets_raw(data.get('planets', {}))

    session['asc_deg'] = asc_deg
    session['planets_raw'] = planets_raw

    d1 = get_d1_chart(planets_raw, asc_deg)
    d3 = get_d3_chart_from_d1(planets_raw, asc_deg)
    d6 = get_d6_chart(planets_raw, asc_deg)
    d9 = get_d9_chart(planets_raw, asc_deg)
    d30 = get_d30_chart(planets_raw, asc_deg)
    d60 = get_d60_chart(planets_raw, asc_deg)

    return render_template(
        'partials/horoscope_charts.html',
        d1=d1, d3=d3, d6=d6, d9=d9, d30=d30, d60=d60
    )

