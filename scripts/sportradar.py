import json
from classes.sportradar import Sportradar

if __name__ == '__main__':
    with open('mock/seasons_tracks.json') as json_file:
        seasons_tracks = json.load(json_file)

        for season in seasons_tracks['season_active']:
            season_id = season['id']
            season_name = season['name']
            season_url = season['url']
            
            sportradar = Sportradar('sportradar', __name__, season_id)
            sportradar.start()
