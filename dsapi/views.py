import uuid
from flask import request, jsonify, abort
from dsapi.core import app, db, queue
from dsapi import classifier


def is_valid_api_key(key):
    matches = db.engine.execute(
        'SELECT COUNT(*) FROM api_keys WHERE key = :key',
        key=key
    ).first()[0]
    return matches > 0


@app.before_request
def before_request():
    """Before requests, check a valid API key given."""

    try:
        api_key = request.headers['X-API-Key']
    except KeyError:
        abort(401, 'No API Key provided')

    if not is_valid_api_key(api_key):
        abort(401, 'Invalid API Key')


@app.route('/predict/feature_a/<feature_a>/feature_b/<feature_b>')
def predict(feature_a, feature_b):

    try:
        feature_a = float(feature_a)
        feature_b = float(feature_b)
    except ValueError:
        abort(400, 'Input features were not valid floats')

    predicted_class, probabilities = classifier.predict(feature_a, feature_b)

    return jsonify({
        'class': predicted_class,
        'class_probabilities': probabilities
    })


@app.route('/predict-slow', methods=['POST'])
def create_prediction():
    body = request.get_json(force=True)
    try:
        feature_a = float(body['feature_a'])
        feature_b = float(body['feature_b'])
    except (TypeError, KeyError, ValueError):
        abort(400, 'Invalid request body')
    id = uuid.uuid4()
    queue.enqueue(
        classifier.predict_slow_and_store,
        id, feature_a, feature_b
    )
    return jsonify({'id': str(id)}), 202


@app.route('/predict-slow/<uuid:id>')
def get_prediction(id):
    query_result = db.engine.execute(
        'SELECT class FROM results WHERE id = :id',
        id=str(id)
    ).first()
    if query_result is None:
        abort(404)
    return jsonify({'class': query_result[0]})
