import re
import dateparser
from datetime import datetime


# from flask_sqlalchemy import SQLAlchemy
# from flask import Flask
# from sqlalchemy import create_engine, text
# import pandas as pd
# import start_up as st


class MyParser:  # parse the user query to extract the location(s) and date(s)
    def __init__(self, decodes, locations_df):
        self.decodes = decodes
        self.locations_df = locations_df
        self.stop_words = {'on', 'be', 'is', 'for', 'and', 'in', 'time'}  # List of stop words to ignore

    def parse_query(self, query):
        # Normalize the query
        query = query.lower()
        # Tokenize the query
        tokens = re.findall(r'\b\w+\b|\S', query)

        sequence = []
        last_parsed_date = None
        location_found = False
        date_found = False
        i = 0
        while i < len(tokens):
            matched = False

            # Try to match multi-word places or date phrases
            for length in range(len(tokens) - i, 0, -1):
                phrase = ' '.join(tokens[i:i + length])

                # Check if the phrase is a known location
                if phrase in self.locations_df['location'].values:
                    sequence.append({'place': phrase})
                    i += length  # Advance by the number of tokens in the matched phrase
                    location_found = True
                    matched = True
                    break

                # Check if the phrase is a known date decode
                if phrase in self.decodes:
                    sequence.append({'date': phrase})
                    last_parsed_date = self.decodes[phrase]
                    i += length  # Advance by the number of tokens in the matched phrase
                    date_found = True
                    matched = True
                    break

                # Skip stop words
                if tokens[i] in self.stop_words:
                    i += 1
                    matched = True
                    break

            if not matched:
                # Parse multi-token dates such as "June 06"
                if i + 1 < len(tokens) and re.match(r'\b\w+\b', tokens[i]) and re.match(r'\b\d+\b', tokens[i + 1]):
                    phrase = ' '.join(tokens[i:i + 2])
                    if len(phrase) > 4:  # reduces chance of dateparser incorrectly creating a date
                        parsed_date = dateparser.parse(phrase, settings={'DATE_ORDER': 'DMY'})

                        if isinstance(parsed_date, datetime):  # convert eg 'June 18' to '2024-06-18'
                            parsed_date = parsed_date.strftime('%Y-%m-%d')

                        if parsed_date and parsed_date in self.decodes:
                            sequence.append({'date': parsed_date})
                            last_parsed_date = parsed_date
                            i += 2  # Advance by two tokens
                            date_found = True
                            matched = True

                if not matched:
                    # Parse single-token dates
                    if len(tokens[i]) > 4:  # reduces chance of dateparser incorrectly creating a date
                        parsed_date = dateparser.parse(tokens[i], settings={'DATE_ORDER': 'DMY'})

                        if isinstance(parsed_date, datetime):  # convert eg 'June 18' to '2024-06-18'
                            parsed_date = parsed_date.strftime('%Y-%m-%d')

                        if parsed_date and parsed_date in self.decodes:
                            if parsed_date.date() != last_parsed_date:
                                sequence.append({'date': parsed_date})
                                last_parsed_date = parsed_date
                            i += 1  # Advance by one token
                            date_found = True
                            matched = True

                    # Check if the phrase is a multi-word place not in stop_words
                    if not matched and i + 1 < len(tokens):
                        next_token = tokens[i + 1]
                        phrase = f"{tokens[i]} {next_token}"
                        if phrase in self.locations_df['location'].values:
                            sequence.append({'place': phrase})
                            i += 2  # Advance by two tokens
                            location_found = True
                            matched = True

            if not matched:
                i += 1  # Advance by one token

        #if location_found and date_found:
        #    return True, grouped_sequence
        #elif not location_found and not date_found:
        return sequence


    def check_sequence(self, sequence):
        i = 0
        n = len(sequence)
        grouped_sequence = []
        group_counter = 1

        while i < n:
            current_group = {'place': [], 'date': []}

            # Rule 1: If the first element is 'place', there may be one or more 'place' elements
            if 'place' in sequence[i]:
                while i < n and 'place' in sequence[i]:
                    current_group['place'].append(sequence[i]['place'])
                    i += 1
                # Rule 2: One or more 'date' elements must follow
                if i < n and 'date' in sequence[i]:
                    while i < n and 'date' in sequence[i]:
                        current_group['date'].append(sequence[i]['date'])
                        i += 1
                    grouped_sequence.append({group_counter: current_group})
                    group_counter += 1
                else:
                    # Convert string dates to datetime objects
                    date_values = [datetime.strptime(date, '%Y-%m-%d') for date in self.decodes.values()]
                    # Get the minimum and maximum dates
                    min_date = min(date_values)
                    max_date = max(date_values)
                    # Convert datetime objects back to string format if needed
                    min_date_str = min_date.strftime('%B %d')
                    max_date_str = max_date.strftime('%B %d')
                    message = f"Please provide a current date.\n" \
                    + f"Forecasts are currently available from {min_date_str} until {max_date_str}.\n" \
                    + "You may wish to use the menu option to refresh your local data."
                    return False, message
            # Rule 4: If the first element is 'date', there may be one or more 'date' elements
            elif 'date' in sequence[i]:
                while i < n and 'date' in sequence[i]:
                    current_group['date'].append(sequence[i]['date'])
                    i += 1
                # Rule 5: One or more 'place' elements must follow
                if i < n and 'place' in sequence[i]:
                    while i < n and 'place' in sequence[i]:
                        current_group['place'].append(sequence[i]['place'])
                        i += 1
                    grouped_sequence.append({group_counter: current_group})
                    group_counter += 1
                else:
                    return False, "Please provide a location."

        if len(grouped_sequence) == 0:
            return False, "Please provide a location and a date."
        else:
            return True, grouped_sequence
