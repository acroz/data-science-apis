import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from rq import Queue
from redis import Redis

from dsapi import errorhandler


app = Flask(__name__)

# Put database in working directory
DATABASE_FILENAME = os.path.join(os.getcwd(), 'database.sqlite')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DATABASE_FILENAME}'

# Not setting SQLALCHEMY_TRACK_MODIFICATIONS causes a DeprecationWarning
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
errorhandler.register(app)

queue = Queue(connection=Redis())
