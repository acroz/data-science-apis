import uuid
from flask import request, jsonify, abort
from dsapi.core import app, db, queue
from dsapi import classifier


def is_valid_api_key(key):
    """Test if a given API key is valid.

    Parameters
    ----------
    key : str
        The key to be tested

    Returns
    -------
    bool
        Indicates if the provided key was valid
    """

    matches = db.engine.execute(
        'SELECT COUNT(*) FROM api_keys WHERE key = :key',
        key=key
    ).first()[0]

    return matches > 0


@app.before_request
def before_request():
    """Before all requests, check a valid API key given."""

    try:
        api_key = request.headers['X-API-Key']
    except KeyError:
        abort(401, 'No API Key provided')

    if not is_valid_api_key(api_key):
        abort(401, 'Invalid API Key')


@app.route('/predict/feature_a/<feature_a>/feature_b/<feature_b>')
def predict(feature_a, feature_b):
    """Simple prediction endpoint returning class for a data point."""

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
    """Submit a slow prediction to the worker queue."""

    # Interpret POST body as JSON, abort with 400 if not possible
    body = request.get_json(force=True)

    # Extract the features from the body
    try:
        feature_a = float(body['feature_a'])
        feature_b = float(body['feature_b'])
    except (TypeError, KeyError, ValueError):
        abort(400, 'Invalid request body')

    # Generate a new UUID identifying the prediction
    id = uuid.uuid4()

    # Queue the prediction
    queue.enqueue(
        classifier.predict_slow_and_store,
        id, feature_a, feature_b
    )

    return jsonify({'id': str(id)}), 202


@app.route('/predict-slow/<uuid:id>')
def get_prediction(id):
    """Retrieve a completed prediction."""

    query_result = db.engine.execute(
        'SELECT class FROM results WHERE id = :id',
        id=str(id)
    ).first()

    if query_result is None:
        # ID does not exist - invalid or prediction does not exist
        abort(404)

    return jsonify({'class': query_result[0]})
