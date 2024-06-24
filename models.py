from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, PrimaryKeyConstraint

db = SQLAlchemy()


# Define the Locations model
class Locations(db.Model):
    __tablename__ = 'locations'  # Explicitly specify the table name
    location_id: Column = Column(Integer, primary_key=True)
    location: Column = Column(String(100), unique=True)
    latitude: Column = Column(Float)
    longitude: Column = Column(Float)


# Define the Weather model
class Weather(db.Model):
    __tablename__ = 'weather'  # Explicitly specify the table name
    location_id = Column(Integer, ForeignKey('locations.location_id'), primary_key=True)
    date = Column(Date, primary_key=True)
    description = Column(String(100))
    degrees_celsius = Column(String(10))

    __table_args__ = (PrimaryKeyConstraint('location_id', 'date'),)


class Decodes(db.Model):
    __tablename__ = 'decodes'
    word: Column = Column(String(50), primary_key=True)
    date: Column = Column(Date, nullable=False)
