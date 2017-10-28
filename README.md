# Data Science API Example

This repository accompanies my talk at PyCon UK 2017, where I gave a tutorial
providing some tips for effective deployment of data science APIs using Flask.

Specifically, my talk demonstrated:

* Flask
* JSON-encoding error handlers
* Authentication with API keys and the `before_request` decorator
* Flask-SQLAlchemy
* Avoiding SQL injection by using SQLAlchmemy's query interpolator
* Worker queues with python-rq
* Deployment with gunicorn

All of these recommendations have been implemented together in this project. In
the near future I will write a blog post or series of posts covering the same
material as my talk - once completed it will be linked here.

## Installation

```sh
$ pip install .
```

To generate the sqlite database:

```sh
$ python gendb.py
```

You will also need to install redis and have it running for the app to function
properly.

With homebrew:

```sh
$ brew install redis
$ brew tap homebrew/services  # If not done previously
$ brew services start redis
```

## Running the Server

Run the api server with:

```sh
$ gunicorn --workers 4 dsapi:app
```

In a separate terminal(s), run one or more python-rq workers:

```sh
rq worker
```

Also make sure that redis-server is running.

## Calling the API

With the server and worker running, the API can be called externally with any
HTTP client. From Python, I recommend using the requests library, available
from PyPI:

```sh
$ pip install requests
```

### Simple Endpoint and Authentication

You can then query the `/predict` endpoint using one of the valid keys in the
`api_keys` table:

```python
>>> import requests
>>> response = requests.get(
>>>     'http://localhost:8000/predict/feature_a/1.0/feature_b/1.0',
>>>     headers={'X-API-Key': 'PE1tlZti1TXJ9nTIri30OnPcquDUpjVrayieAAzY'}
>>> )
>>> response.status_code
200
>>> response.json()
{'class': 1, 'class_probabilities': [0.0961415144762564, 0.9038584855237436]})
```

Note how missing or invalid API keys will return a `401 UNAUTHORIZED` response:

```python
>>> response = requests.get(
>>>     'http://localhost:8000/predict/feature_a/1.0/feature_b/1.0',
>>>     headers={'X-API-Key': 'invalid-key'}
>>> )
>>> response.status_code
401
>>> response.json()
{'error': True, 'message': 'Invalid API Key'}
```

### Slow Task Endpoints

The `/predict-slow` endpoint accepts a `POST` request with the features in the
body and returns an ID field that can be redeemed later for the result:

```python
>>> response = requests.post()
>>>     'http://localhost:8000/predict-slow',
>>>     json={'feature_a': 1.3, 'feature_b': -3.2},
>>>     headers={'X-API-Key': 'PE1tlZti1TXJ9nTIri30OnPcquDUpjVrayieAAzY'}
>>> )
>>> response.status_code
202
>>> response.json()
{'id': 'a779fb1a-8811-48f2-b79e-00f223bb9f43'}
```

To check for the result:

```python
>>> id = response.json()['id']
>>> response = requests.get(
>>>     f'http://localhost:8000/predict-slow/{id}',
>>>     headers={'X-API-Key': 'PE1tlZti1TXJ9nTIri30OnPcquDUpjVrayieAAzY'}
>>> )
```

Before the result is ready this will yield a `404 NOT FOUND`:

```
>>> response.status_code
404
```

Once ready, the result will be returned with a `200 OK` response:

```
>>> response.status_code
200
>>> response.json()
{'class': 0}
```
