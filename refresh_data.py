from sqlalchemy.sql import text
from models import Locations
import requests
import csv
from datetime import datetime
from temp_api_key import TempApiKey


def refresh_data(app, db):

    refresh_locations(app, db)
    refresh_weather(app, db)
    refresh_decodes(app, db)


def refresh_locations(app, db):

    with app.app_context():
        db.create_all()  # on initial run, create database and tables

        # Truncate the locations table
        db.session.execute(text("DELETE FROM locations"))
        db.session.commit()

        try:
            with open("locations.csv") as f:
                reader = csv.reader(f)
                next(reader)
                for row in reader:
                    new_entry = Locations(
                        location_id=row[0],
                        location=row[1],
                        latitude=float(row[2]),
                        longitude=float(row[3]))
                    db.session.add(new_entry)
                db.session.commit()


        except Exception as er:
            # Handle exceptions
            error_text = "<p>The error:<br>" + str(er) + "</p>"
            state = '<h1>The Connection unsuccessful.</h1>'
            print(state + error_text)
            return state + error_text


def refresh_weather(app, db):
    api_key = TempApiKey.get_api_key()
    base_url = "https://api.openweathermap.org/data/2.5/forecast"

    try:
        with app.app_context():
            # Truncate the weather table
            db.session.execute(text("DELETE FROM weather"))
            db.session.commit()

            # Get the locations
            locations = db.session.execute(text('SELECT * FROM locations')).fetchall()

        with app.app_context():

            for location in locations:
                # openweather API.  Get the weather for each location.
                response = requests.get(
                    f"{base_url}?lat={location.latitude}&lon={location.longitude}&appid={api_key}&units=metric")
                response_json = response.json()

                for entry in response_json['list']:
                    unix_timestamp = entry['dt']
                    dt = datetime.fromtimestamp(unix_timestamp)
                    # Check if the hour is 15 (3 PM)
                    if dt.hour != 13:
                        continue
                    # Convert Unix timestamp to datetime
                    timestamp = entry['dt']
                    xdate = datetime.utcfromtimestamp(timestamp).date()
                    date = xdate
                    description = entry['weather'][0]['description']
                    temp_celsius = round(entry['main']['temp'])

                    # Insert weather data into the database
                    sql = text(
                        "INSERT INTO weather (location_id, date, description, degrees_celsius) \
                            VALUES (:location_id, :date, :description, :degrees_celsius)")
                    db.session.execute(sql, {
                        'location_id': location.location_id,
                        'date': date,
                        'description': description,
                        'degrees_celsius': f"{temp_celsius}°C"
                    })
            db.session.commit()

        return 'something'

    except Exception as er:
        # Handle exceptions
        error_text = "<p>The error:<br>" + str(er) + "</p>"
        state = '<h1>Connection unsuccessful.</h1>'
        return state + error_text


def refresh_decodes(app, db):
    try:
        with app.app_context():
            # Truncate the weather table
            db.session.execute(text("DELETE FROM decodes"))
            db.session.commit()

            decodess = get_decodess(db)

            # Insert decodes data into the database
            for word, date in decodess.items():
                sql = text("INSERT INTO decodes (word, date) VALUES (:word, :date)")
                db.session.execute(sql, {'word': word, 'date': date})
            db.session.commit()
        return 'hello'

    except Exception as er:
        # Handle exceptions
        error_text = "<p>The error:<br>" + str(er) + "</p>"
        state = '<h1>The Connection unsuccessful.</h1>'
        print(state + error_text)
        return state + error_text


def get_decodess(db):
    # Fetch dates from the database
    dates = db.session.execute(text('SELECT DISTINCT date FROM weather')).fetchall()

    # Convert to list of date strings
    date_strings = [date[0] for date in dates]

    decodess1 = {
        'today': date_strings[0],
        'tomorrow': date_strings[1],
        '2 days': date_strings[2],
        '3 days': date_strings[3],
        '4 days': date_strings[4],
        date_strings[0]: date_strings[0],
        date_strings[1]: date_strings[1],
        date_strings[2]: date_strings[2],
        date_strings[3]: date_strings[3],
        date_strings[4]: date_strings[4]
    }

    # Create a dictionary with day name as the key and date string as the value
    decodess2 = {datetime.strptime(date_str, '%Y-%m-%d').strftime('%A'): date_str for date_str in date_strings}
    decodess = {**decodess1, **decodess2}

    return decodess
