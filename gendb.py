import pandas
from sklearn.datasets import make_classification

from dsapi.core import db


# Generate some training data
features, classes = make_classification(
    n_samples=100,
    n_features=2,
    n_classes=2,
    n_informative=2,
    n_redundant=0
)

# Create data table
data = pandas.DataFrame({
    'feature_a': features[:, 0],
    'feature_b': features[:, 1],
    'class': classes
})
data.to_sql('data', db.engine)

# Create results table
db.engine.execute("""
    CREATE TABLE results (
        id TEXT UNIQUE NOT NULL,
        class INTEGER
    );
""")

# Create API key table
api_keys = pandas.DataFrame({
    'key': [
        'PE1tlZti1TXJ9nTIri30OnPcquDUpjVrayieAAzY',
        '4jp1YQZYB5q0Rgd6ddDdAqbhTVSrOkLscmSaXnnW'
    ]
})
api_keys.to_sql('api_keys', db.engine)
