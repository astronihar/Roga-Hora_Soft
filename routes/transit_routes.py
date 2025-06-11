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







transit_routes = Blueprint('transit_routes', __name__)






@transit_routes.route('/transit')
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
        'transit.html',
        transit={'D1': chart_live},
        fixed_chart={'D1': chart_moon},
        planet_table=data['planets'],
        ascendant=data['ascendant'],
        data=data
    )