from flask import Flask, render_template, request, jsonify
from geopy.geocoders import Nominatim
from logic.divisionalLogic import  get_d3_chart_from_d1, get_d6_chart, get_d9_chart, get_d30_chart, get_d60_chart
import swisseph as swe
import datetime
import sqlite3
import hashlib
import json
import pandas as pd
import re


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
