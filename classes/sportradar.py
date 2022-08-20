import json
from utils.league.history import team_matches_url
from utils.league.history import season_team_list
from utils.league.history import scrapped_match
from utils.league.history import update_next_matches
from utils.config.mongo import make_mongo_con, save
from utils.scrapper import season_data


class Sportradar:
    def __init__(self, country, league_name, season):
        self.connection = make_mongo_con().sportradar
        self.country = country
        self.league_name = league_name
        self.season = season
        self.interval_for_request = 10

    def start(self):
        season_data(self.country, self.league_name, self.season)
        self._insert_data_to_mongodb(self.country, self.league_name, self.season)



    def _insert_data_to_mongodb(self, country, league_name, season):
        with open(f'data/{country}/{league_name}/{season}.json') as json_file:
            data = json.load(json_file)


            for team in data['teams']:
                if self.connection.team.find({ 'id': int(team['id']) }).count() == 0:
                    save(self.connection, 'team', team)


            for match_id in data['matches'].keys():
                if self.connection.matches.find({ 'match': int(match_id) }).count() == 0:
                    save(self.connection, 'matches', data['matches'][match_id])

                if self.connection.matches.find({ 'match': int(match_id), 'finished': False }).count() == 1:
                    self.connection.matches.remove({ 'match': int(match_id), 'finished': False})
                    save(self.connection, 'matches', data['matches'][match_id])