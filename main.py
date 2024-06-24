from flask import render_template, request, redirect, url_for, jsonify
from datetime import datetime
from sqlalchemy.sql import text
import os
import pandas as pd
import string
from my_parser import MyParser
from reply import Reply
import refresh_data as r
import utils as u
import start_up as st
import get_local_data_once as d

basedir = os.path.abspath(os.path.dirname(__file__))
db_name = 'weather.sqlite3'

# initialise app and database connection
app, db, engine = st.start_up(basedir, db_name)


# read database tables once only
decodes, display_decodes, locations_df, weather_df = d.get_local_data_once(app, db, engine)
# when window opens display welcome text
welcome = True


@app.route("/")
def home():
    locations = [string.capwords(location) for location in locations_df['location']]
    return render_template("index.html", locations=locations)


@app.route("/get")
def get_bot_response():
    query = request.args.get('msg')
    global welcome  # Declare welcome as a global variable
    name = u.get_last_word(query)
    if welcome:
        welcome = False
        return f"Welcome {name.capitalize()}. How can I help you with your weather enquiry today?"
    else:
        parser = MyParser(decodes, locations_df)
        parsed_sequence = parser.parse_query(query)
        result, grouped_sequence = parser.check_sequence(parsed_sequence)

        if result:
            reply = Reply(app, db, engine, decodes, locations_df, weather_df, grouped_sequence)
            bot_response = reply.get_weather()
            return '\n\n'.join(bot_response)
        else:
            return grouped_sequence  # 'grouped_sequence' will be a missing location or date message


@app.route("/current-dates")
def current_dates():
    return jsonify(display_decodes)


@app.route("/refresh-data")
def refresh_data():  # Refresh local data the openweather API

    global decodes, display_decodes, locations_df, weather_df

    r.refresh_data(app, db)
    # refresh: read database tables once only
    decodes, display_decodes, locations_df, weather_df = d.get_local_data_once(app, db, engine)

    return "Data refreshed successfully", 200


if __name__ == '__main__':
    app.run(debug=True)
