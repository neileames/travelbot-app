from flask import Flask, render_template, request
from models import db
import os
from sqlalchemy import create_engine

def start_up(basedir, db_name):
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, db_name)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize the SQLAlchemy object with the app
    db.init_app(app)

    # Create the SQLAlchemy engine
    engine = create_engine('sqlite:///' + os.path.join(basedir, db_name))

    return app, db, engine
