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


api_location = Blueprint('api_location', __name__)


@api_location.route('/api/states')
def api_states():
    query = request.args.get("query", "").lower()
    states = city_df['state'].dropna().unique()
    suggestions = [s for s in states if query in s.lower()]
    return jsonify({"suggestions": suggestions})


@api_location.route('/api/cities')
def api_cities():
    state = request.args.get("state", "")
    query = request.args.get("query", "").lower()
    cities = city_df[city_df['state'].str.lower() == state.lower()]['city'].dropna().unique()
    suggestions = [c for c in cities if query in c.lower()]
    return jsonify({"suggestions": suggestions})