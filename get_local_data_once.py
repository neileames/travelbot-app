from datetime import datetime
from sqlalchemy.sql import text
import pandas as pd


def get_local_data_once(app, db, engine):

    decodes, display_decodes = get_decodes(app, db)
    locations_df = pd.read_sql_table('locations', engine)
    locations_df['location'] = locations_df['location'].str.lower()
    weather_df = pd.read_sql_table('weather', engine)

    return decodes, display_decodes, locations_df, weather_df

def get_decodes(app, db):
    with app.app_context():
        # Fetch all records from the 'decodes' table
        decodes = db.session.execute(text('SELECT word, date FROM decodes')).fetchall()

        # Remove entries where the key is equal to the value
        removed_decodes = [(word, date) for word, date in decodes if word.lower() != date]

        # Sort decodes by date first, then by word
        sorted_decodes = sorted(removed_decodes, key=lambda x: (x[1], x[0]))

        # Reformat dates and create display_decodes with capitalized keys
        display_decodes = {}
        for word, date in sorted_decodes:
            date_obj = datetime.strptime(date, '%Y-%m-%d')
            formatted_date = date_obj.strftime('%d %b %Y')
            display_decodes[word.capitalize()] = formatted_date

        # Create decodes with lowercase keys
        decodes = {word.lower(): date for word, date in decodes}

    return decodes, display_decodes
