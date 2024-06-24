class TempApiKey:

    @staticmethod
    def get_api_key(key='OpenWeather_API_key'):
        # temporary replacement for environment variables
        api_key = {
            'OpenWeather_API_key': '<your_API_key>'
        }
        return api_key[key]
