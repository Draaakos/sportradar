import json
import time
from classes.sportradar import Sportradar

if __name__ == '__main__':
    with open('mock/seasons_tracks.json') as json_file:
        seasons_tracks = json.load(json_file)

        for season in seasons_tracks['season_active']:
            season_id = season['id']
            season_name = season['name']
            season_url = season['url']
            season_country = season['country']
            
            sportradar = Sportradar(season_country, season_name, season_id)
            sportradar.start()
            time.sleep(5)
