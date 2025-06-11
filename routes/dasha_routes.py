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



dasha_routes = Blueprint('dasha_routes', __name__)


@dasha_routes.route('/dasha')
def dasha():
    from logic.dashalogic import get_full_dasha_from_session
    data = get_full_dasha_from_session()
    return render_template('dasha.html', dasha_data=data)


