import os
import certifi
from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)

mongo_uri = os.getenv('MONGODB_URI')
if not mongo_uri:
    raise RuntimeError("Falta MONGODB_URI")

client = MongoClient(mongo_uri, tlsCAFile=certifi.where())
db = client['gamehub']
reviews_col = db['reviews']

@app.route('/api/reviews', methods=['POST'])
def add_review():
    data = request.get_json()
    required_fields = ['videojuego_id', 'usuario', 'calificacion']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Faltan campos obligatorios'}), 400
    review = {
        'videojuego_id': data['videojuego_id'],
        'usuario': data['usuario'],
        'comentario': data.get('comentario', ''),
        'calificacion': data['calificacion'],
        'fecha': datetime.utcnow()
    }
    reviews_col.insert_one(review)
    return jsonify({'message': 'Reseña registrada en analítica'}), 201

@app.route('/api/stats', methods=['GET'])
def get_stats():
    videojuego_id = request.args.get('videojuego_id')
    if not videojuego_id:
        return jsonify({'error': 'Falta videojuego_id'}), 400
    try:
        videojuego_id = int(videojuego_id)
    except ValueError:
        return jsonify({'error': 'videojuego_id debe ser entero'}), 400

    pipeline = [
        {'$match': {'videojuego_id': videojuego_id}},
        {'$group': {
            '_id': '$videojuego_id',
            'total_reviews': {'$sum': 1},
            'average_rating': {'$avg': '$calificacion'}
        }}
    ]
    try:
        result = list(reviews_col.aggregate(pipeline))
    except Exception as e:
        return jsonify({'error': f'Error en agregación: {str(e)}'}), 500
    if not result:
        return jsonify({'total_reviews': 0, 'average_rating': 0})
    stats = result[0]
    return jsonify({
        'total_reviews': stats['total_reviews'],
        'average_rating': round(stats['average_rating'], 2)
    })

@app.route('/api/health')
def health():
    try:
        client.admin.command('ping')
        return jsonify({'status': 'ok', 'mongodb': 'conectado'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
