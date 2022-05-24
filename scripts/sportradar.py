import requests

class Sportradar:
    def __init__(self, filename, name):
        self.name = name

    def start(self):
        print(self._fetch_data('https://stats.fn.sportradar.com/sportradar/es/Europe:Berlin/gismo/stats_season_injuries/83872'))


    def _fetch_data(self, url):
        response = requests.get(url).json()
        return response


if __name__ == '__main__':
    scrapper = Sportradar('sportradar', __name__)
    scrapper.start()