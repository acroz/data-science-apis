import time

import numpy
import pandas
from sklearn.linear_model import LogisticRegression

from dsapi.core import db


def _train_model():
    """Train a logistic regression classifier using data in the database.

    Returns
    -------
    sklearn.linear_model.LogisticRegression
        The trained classifier
    """

    data = pandas.read_sql('SELECT * FROM data', db.engine)

    # Extract features and classes from query result
    features = numpy.array(data[['feature_a', 'feature_b']])
    classes = numpy.array(data['class'])

    # Train the model
    model = LogisticRegression()
    model.fit(features, classes)

    return model


# Prepare a model at module import time
# This approach implies that the data we are training to in _train_model never
# changes. Where this assumption is not valid, more complex caching logic or
# retraining the model for each request may be necessary.
MODEL = _train_model()


def predict(feature_a, feature_b):
    """Predict the class for a data point.

    Parameters
    ----------
    feature_a : float
    feature_b : float

    Returns
    -------
    int
        The predicted class
    list of float
        The probabilities of the data point being all classes
    """

    features = numpy.array([[feature_a, feature_b]])

    predicted_class = int(MODEL.predict(features)[0])
    probabilities = [float(p) for p in MODEL.predict_proba(features)[0]]

    return predicted_class, probabilities


def predict_slow(feature_a, feature_b):
    """Like `predict()`, but slower."""
    time.sleep(5)
    return predict(feature_a, feature_b)


def predict_slow_and_store(id, feature_a, feature_b):
    """Call `predict_slow()` and store the result in the database.

    Parameters
    ----------
    id : uuid.UUID
        The id to store the result as in the database
    feature_a : float
    feature_b : float
    """

    predicted_class, _ = predict_slow(feature_a, feature_b)

    db.engine.execute(
        'INSERT INTO results (id, class) VALUES (:id, :class_)',
        id=str(id),
        class_=predicted_class
    )
