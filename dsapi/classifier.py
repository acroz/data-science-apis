import numpy
import time
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression

from dsapi.core import db


def _train_model():

    X, y = make_classification(
        n_samples=100,
        n_features=2,
        n_classes=2,
        n_informative=2,
        n_redundant=0
    )

    model = LogisticRegression()
    model.fit(X, y)

    return model


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
    """Call `predict_slow()` and store the result in the database."""
    predicted_class, _ = predict_slow(feature_a, feature_b)
    db.engine.execute(
        'INSERT INTO results (id, class) VALUES (:id, :class_)',
        id=str(id),
        class_=predicted_class
    )
