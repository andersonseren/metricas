import os
import certifi
from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)

mongo_uri = os.getenv('MONGODB_URI')
if not mongo_uri:
    raise RuntimeError("Falta MONGODB_URI")

# Conexión segura usando los certificados de certifi
client = MongoClient(mongo_uri, tlsCAFile=certifi.where())
db = client['gamehub']
reviews_col = db['reviews']

# ... (el resto del código igual: /api/reviews, /api/stats, /api/health)
