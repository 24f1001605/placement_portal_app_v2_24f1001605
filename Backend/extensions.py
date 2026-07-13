from flask_security import SQLAlchemyUserDatastore
from models import db, User, Role
from celery import Celery
from flask_caching import Cache

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
celery = Celery()
cache = Cache()
