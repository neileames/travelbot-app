import random
import string


class Reply:  # parse the user query to extract the location(s) and date(s)
    def __init__(self, app, db, engine, decodes, locations_df, weather_df, grouped_sequence):
        self.app = app
        self.db = db
        self.engine = engine
        self.decodes = decodes
        self.locations_df = locations_df
        self.weather_df = weather_df
        self.grouped_sequence = grouped_sequence

    def get_weather(self):

        reply = []

        temperature_text = [
            'The expected maximum temperature is',
            'The maximum forecast temperature is',
            'The forecast maximum temperature is'
        ]

        prepositions = {
            'today': '',
            'tomorrow': '',
            '2 days': 'in',
            '3 days': 'in',
            '4 days': 'in',
        }

        with self.app.app_context():
            for group in self.grouped_sequence:
                for key, sequence in group.items():
                    places = sequence['place']
                    dates = sequence['date']
                    for place in places:
                        # Get location_id for the place
                        location_id = self.locations_df.loc[
                            self.locations_df['location'].str.lower() == place.lower(), 'location_id'].values[0]

                        for date in dates:
                            decoded_date = self.decodes[date]
                            wd = []  # weather details for each location/date
                            weather = self.weather_df[
                                (self.weather_df['location_id'] == location_id) & (
                                            self.weather_df['date'] == decoded_date)]
                            wd.append({
                                'place': place,
                                'date': date,
                                'description': weather.iloc[0]['description'],
                                'degrees_celsius': weather.iloc[0]['degrees_celsius']
                            })

                            prep = prepositions.get(date, 'on')  # 'not found' is the default value

                            days_of_week = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday',
                                            'saturday']

                            for i in range(0, len(wd)):

                                if wd[i]['date'] in days_of_week:
                                    wd[i]['date'] = wd[i]['date'].capitalize()

                                reply_no = random.randint(0, 1)

                                if reply_no == 1 and wd[i]['date'] in ['today', 'tomorrow']:
                                    wd[i]['date'] = wd[i]['date'].capitalize()

                                replies = [
                                    f"In {string.capwords(wd[i]['place'])} {prep} {wd[i]['date']} the forecast is for {wd[i]['description']}. {temperature_text[random.randint(0, 2)]} {wd[i]['degrees_celsius']} .",
                                    f"{string.capwords(prep)} {wd[i]['date']} in {string.capwords(wd[i]['place'])} the forecast is for {wd[i]['description']}. {temperature_text[random.randint(0, 2)]} {wd[i]['degrees_celsius']} ."
                                ]
                                reply.append(replies[reply_no])
        return reply
