class TempApiKey:

    @staticmethod
    def get_api_key(key='OpenWeather_API_key'):
        # temporary replacement for environment variables
        api_key = {
            'OpenWeather_API_key': 'a59899315ab0a08ca2c90b4339769690'
        }
        return api_key[key]
