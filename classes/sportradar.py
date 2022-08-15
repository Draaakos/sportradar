import json
import time
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


    # def _start(self):
    #     season_team_list_response = season_team_list(self.season)
    #     team_list = season_team_list_response['team_list']
    #     max_rounds = season_team_list_response['max_rounds']
    #     league_name = season_team_list_response['name']

    #     # make a new json file or fetch the information if exist in the data folder
    #     season_file_data = team_matches_url(self.season, team_list, league_name, max_rounds)

    #     for round_key in season_file_data['matches'].keys():
    #         for match in season_file_data['matches'][round_key].values():
    #             if not match["id"] in season_file_data['matches_scanned']:
    #                 season_file_data['matches'][round_key][f'{match["id"]}']['information'] = scrapped_match(match)
    #                 season_file_data['matches_scanned'].append(match["id"])

    #                 new_season_file_data = json.dumps(season_file_data, indent=4)
    #                 with open(f'data/{league_name}/{self.season}.json', 'w') as json_file:
    #                     json_file.write(new_season_file_data)
    #                 time.sleep(self.interval_for_request)


    #     with open(f'data/{league_name}/{self.season}.json') as json_file:
    #         json_information = json.load(json_file)
    #         json_information['next_matches'] = update_next_matches(season_file_data['matches_scanned'], self.season)

    #         json_to_file = json.dumps(json_information, indent=4)
    #         with open(f'data/{league_name}/{self.season}.json', 'w') as new_json_file:
    #             new_json_file.write(json_to_file)

    #     self._insert_data_to_mongodb(league_name, self.season)



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