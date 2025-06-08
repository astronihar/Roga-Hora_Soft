from flask import Flask, render_template, request, jsonify
from geopy.geocoders import Nominatim
import swisseph as swe
import datetime
import sqlite3
import hashlib
import json
import pandas as pd
import re

from logic.birth_form_logic import *
from logic.astronihar_api_calc import *
from logic.divisional import *
from app import app



