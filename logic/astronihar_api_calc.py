from flask import Flask, render_template, request, jsonify
from geopy.geocoders import Nominatim
from logic.divisional import get_d3_chart, get_d6_chart, get_d9_chart, get_d30_chart, get_d60_chart
import swisseph as swe
import datetime
import sqlite3
import hashlib
import json
import pandas as pd
import re

from logic.birth_form_logic import *



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