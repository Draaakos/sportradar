import time
import requests
from jsonschema import validate
# from schema import Schema, And, Use, Optional, SchemaError, Forbidden
from dto.match import Match
from dto.league import League
from dto.team import Team
from dto.player import Player
from dto.stat import Stat
from . import utils


class Structure:
    def __init__(self, obj, config):
        self.error_list = []
        self._check(obj, config)

    def _check(self, obj, config):
        try:
            for structure in config.items():
                structure_key   = structure[0]
                structure_value = structure[1]
                
                if not obj[structure_key]:
                    self.error_list.append('error')
                    return

                if obj[structure_key] is None:
                    self.error_list.append(structure_key)
                    return

                if structure_value != type(obj[structure_key]):
                    if type(structure_value) != type(obj[structure_key]):
                        self.error_list.append(structure_key)
                
                if type(structure_value) == dict:
                    self._check(obj[structure_key], config[structure_key])

        except KeyError:
            self.error_list.append('Key Error')

    def is_valid(self):
        if len(self.error_list):
            print('error list', self.error_list)
        return True if len(self.error_list) == 0 else False



def validation(obj):
    structure = {
        'header': {
            'teams': list
        },
        'general': {
            'matchId': str,
            'matchName': str,
            'matchRound': str,
            'leagueId': int,
            'leagueName': str,
            'matchTimeUTC': str,
            'homeTeam': {
                'name': str,
                'id': int
            },
            'awayTeam': {
                'name': str,
                'id': int
            }
        },
        'content': {
            'lineup': {
                'lineup': list,
                'teamRatings': {
                    'home': {
                        'num': float
                    },
                    'away': {
                        'num': float
                    }
                }
            },
            'stats': {
                'stats': list
            }
        }
    }

    return Structure(obj, structure).is_valid()


def process_stats(raw_stats):
    group_keys = [
        'top_stats', 
        'shots', 
        'passes', 
        'defence', 
        'duels', 
        'discipline'
    ]

    stats_keys = [
        'ball_possession',
        'total_shots',
        'shots_off_target',
        'shots_on_target',
        'blocked_shots',
        'red_cards',
        'yellow_cards',
        'big_chances',
        'big_chances_missed',
        'corners',
        'passes',
        'keeper_saves'
    ]

    stats = {}
    for stat in raw_stats:
        stats[stat['title'].lower().replace(' ', '_')] = {}
        
        for item_stat in stat['stats']:
            stats[stat['title'].lower().replace(' ', '_')][item_stat['title'].lower().replace(' ', '_')] = item_stat['stats']

    keys_validated = 0
    for key in group_keys:
        if key in stats.keys():
            keys_validated += 1

            for stat_key in stats[key].keys():
                if stat_key in stats_keys:
                    keys_validated += 1
    
    if keys_validated >= (len(group_keys) + len(stats_keys)):
        return stats
    else:
        return None


class Fotmob():
    def __init__(self, filename, name):
        self.match_list = []
        self.team_list = []


        self.filename = filename
        self.connection = utils.make_mongo_con().futbol_analisis_1_3
        self.logger = utils.create_logger(filename, name)
        self.headers = {
            'User-Agent': 'PostmanRuntime/7.29.0'
        }

    # def start(self):
    #     x = requests.get('https://www.fotmob.com/matchDetails?matchId=3657190').json()
    #     validation(x)
    #     print(x)

    def start(self):
        # 'https://www.fotmob.com/leagues?ccode3=CHL&timezone=America%2FSantiago&id=87&tab=matches&seo=laliga'

        # este es el correcto
        league_url_list = [     
            # 'https://www.fotmob.com/leagues?ccode3=CHL&timezone=America%2FSantiago&id=47&tab=matches&seo=mls',
            # 'https://www.fotmob.com/leagues?ccode3=CHL&timezone=America%2FSantiago&id=53&tab=matches&seo=mls',
            # 'https://www.fotmob.com/leagues?ccode3=CHL&timezone=America%2FSantiago&id=54&tab=matches&seo=mls',
            # 'https://www.fotmob.com/leagues?ccode3=CHL&timezone=America%2FSantiago&id=87&tab=matches&seo=mls',
            # 'https://www.fotmob.com/leagues?ccode3=CHL&timezone=America%2FSantiago&id=55&tab=matches&seo=mls',
            # 'https://www.fotmob.com/leagues?ccode3=CHL&timezone=America%2FSantiago&id=57&tab=matches&seo=mls',
            # 'https://www.fotmob.com/leagues?ccode3=CHL&timezone=America%2FSantiago&id=40&tab=matches&seo=mls',
            # 'https://www.fotmob.com/leagues?ccode3=CHL&timezone=America%2FSantiago&id=61&tab=matches&seo=mls',
            # 'https://www.fotmob.com/leagues?ccode3=CHL&timezone=America%2FSantiago&id=69&tab=matches&seo=mls',
            # 'https://www.fotmob.com/leagues?ccode3=CHL&timezone=America%2FSantiago&id=48&tab=matches&seo=mls',
            # 'https://www.fotmob.com/leagues?ccode3=CHL&timezone=America%2FSantiago&id=86&tab=matches&seo=mls',
            # 'https://www.fotmob.com/leagues?ccode3=CHL&timezone=America%2FSantiago&id=108&tab=matches&seo=mls',
            # 'https://www.fotmob.com/leagues?ccode3=CHL&timezone=America%2FSantiago&id=109&tab=matches&seo=mls',
            'https://www.fotmob.com/leagues?ccode3=CHL&timezone=America%2FSantiago&id=110&tab=matches&seo=mls',
            'https://www.fotmob.com/leagues?ccode3=CHL&timezone=America%2FSantiago&id=273&tab=matches&seo=mls',



            # 'https://www.fotmob.com/leagues?ccode3=CHL&timezone=America%2FSantiago&id=8982&tab=matches&seo=mls',
            # 'https://www.fotmob.com/leagues?ccode3=CHL&timezone=America%2FSantiago&id=8983&tab=matches&seo=mls'
            


            # 'https://www.fotmob.com/leagues?ccode3=ARG&timezone=America%2FBuenos_Aires&id=47&tab=overview&seo=premier-league',
            # 'https://www.fotmob.com/leagues?ccode3=ARG&timezone=America%2FBuenos_Aires&id=53&tab=overview&seo=ligue-1',
            # 'https://www.fotmob.com/leagues?ccode3=ARG&timezone=America%2FBuenos_Aires&id=54&tab=overview&seo=1.-bundesliga',
            # 'https://www.fotmob.com/leagues?ccode3=ARG&timezone=America%2FBuenos_Aires&id=87&tab=overview&seo=laliga',
            # 'https://www.fotmob.com/leagues?ccode3=ARG&timezone=America%2FBuenos_Aires&id=55&tab=overview&seo=serie-a',
            # 'https://www.fotmob.com/leagues?ccode3=ARG&timezone=America%2FBuenos_Aires&id=57&tab=overview&seo=eredivisie',
            # 'https://www.fotmob.com/leagues?ccode3=ARG&timezone=America%2FBuenos_Aires&id=40&tab=overview&seo=first-division-a',
            # 'https://www.fotmob.com/leagues?ccode3=ARG&timezone=America%2FBuenos_Aires&id=61&tab=overview&seo=liga-portugal',
            # 'https://www.fotmob.com/leagues?ccode3=ARG&timezone=America%2FBuenos_Aires&id=69&tab=overview&seo=super-league' 
        ]

        for url in league_url_list:
            response = self._fetch_data_league(url)
            league_id = response['details']['id']

            is_exist = self.connection.league.find_one({ "information.id": int(league_id) })
            if is_exist is None:
                league = League()
                league.id = league_id
                league.name = response['details']['name']
                league.short_name = response['details']['shortName']
                self._save('league', league)
                
            for item in response['matchesTab']['data']['allMatches']:
                if not item['id'] in self.match_list:
                    if item['status']['finished']:
                        self.match_list.append(item['id'])

                if not item['home']['id'] in self.team_list:
                    self.team_list.append(item['home']['id'])

            
            for team_id in self.team_list:
                self._process_team(team_id)


            for match_id in self.match_list:
                self._process_match(match_id)


            #     print('guardando...')
            #     team = Team()
            #     team.id = team_id
            #     team.name = 'TEst'
            #     self._save('team2', team)


                # print(item['status'])
                # print('')

        # print(self.match_list)
        # print(self.team_list)





    def _process_match(self, match_id):
        is_exist = self.connection.match.find_one({ "information.id": int(match_id) })

        url = f"https://www.fotmob.com/matchDetails?matchId={match_id}"

        # is_banned = 

        if is_exist is None:
            print(url)
            time.sleep(1) 
            data = requests.get(url).json()

            if validation(data) is False:
                # self._save('ban', { 'url': url })
                return
            else:
                return self._process_data_detail(data)
        # else:
        #     pass
        #     print('ya esta registrado')








    def _process_team(self, team_id):
        is_exist = self.connection.team.find_one({ "information.id": team_id })

        if is_exist is None:
            url = f"https://www.fotmob.com/teams?ccode3=CHL&timezone=America%2FSantiago&id={team_id}&tab=stats"
            data = requests.get(url).json()

            team = Team()
            team.id = team_id
            team.name = data['details']['name']
            team.short_name = data['details']['shortName']
            self._save('team', team)
            print(f"saving - {data['details']['name']}")




    def _start(self):
        league_url_list = [
            'https://www.fotmob.com/leagues?ccode3=ARG&timezone=America%2FBuenos_Aires&id=47&tab=overview&seo=premier-league',
            'https://www.fotmob.com/leagues?ccode3=ARG&timezone=America%2FBuenos_Aires&id=53&tab=overview&seo=ligue-1',
            'https://www.fotmob.com/leagues?ccode3=ARG&timezone=America%2FBuenos_Aires&id=54&tab=overview&seo=1.-bundesliga',
            'https://www.fotmob.com/leagues?ccode3=ARG&timezone=America%2FBuenos_Aires&id=87&tab=overview&seo=laliga',
            'https://www.fotmob.com/leagues?ccode3=ARG&timezone=America%2FBuenos_Aires&id=55&tab=overview&seo=serie-a',
            'https://www.fotmob.com/leagues?ccode3=ARG&timezone=America%2FBuenos_Aires&id=57&tab=overview&seo=eredivisie',
            'https://www.fotmob.com/leagues?ccode3=ARG&timezone=America%2FBuenos_Aires&id=40&tab=overview&seo=first-division-a',
            'https://www.fotmob.com/leagues?ccode3=ARG&timezone=America%2FBuenos_Aires&id=61&tab=overview&seo=liga-portugal',
            'https://www.fotmob.com/leagues?ccode3=ARG&timezone=America%2FBuenos_Aires&id=69&tab=overview&seo=super-league'
        ]


        for url in league_url_list:
            data = self._fetch_data_league(url)

            for index, team_data in enumerate(data['tableData'][0]['table']['all']):
                name_data = team_data['pageUrl'].split('/overview/')[-1]

                team_found = self.connection.team.remove({ "information.id": team_data['id'] })

                team = Team()
                team.id = team_data['id']
                team.name = team_data['name']
                team.name_data = name_data
                team.url = f"https://www.fotmob.com/{team_data['pageUrl']}"
                team.played = team_data['played']
                team.wins = team_data['wins']
                team.draws = team_data['draws']
                team.losses = team_data['losses']
                team.points = team_data['pts']
                team.position = index + 1
                self._save('team', team)

                url = f"https://www.fotmob.com/teams?ccode3=ARG&timezone=America%2FBuenos_Aires&id={team_data['id']}&tab=squad&seo={name_data}"
                print('team => ', url)
                squad_list = requests.get(url).json()
                self._process_squad(squad_list)
                # time.sleep(0.2)


    def _fetch_data_league(self, url):
        print('league => ', url)
        response = requests.get(url).json()
        return response


    def _process_squad(self, squad_list):
        goalkeepers = squad_list['squad'][1][1]
        defenders = squad_list['squad'][2][1]
        midfielders = squad_list['squad'][3][1]
        attackers = squad_list['squad'][4][1]
        
        squad_list = goalkeepers + defenders + midfielders + attackers
        for player in squad_list:
            self._process_player(player)
            # time.sleep(0.2)


    def _process_player(self, player_data):
        leagues_availables = [
            'Premier League', 
            'Ligue 1', 
            'LaLiga', 
            '1. Bundesliga', 
            'Serie A',
            'Eredivisie',
            'First Division A',
            'Liga Portugal',
            'Super Lig'
        ]

        # try:
        url = f"https://www.fotmob.com/playerData?id={player_data['id']}"
        print('player => ', url)
        data = requests.get(url).json()

        if data['recentMatches']:
            player = Player()
            player.id = data['id']
            player.name = data['name']
            player.team_id = data['origin']['teamId']
            player.team_name = data['origin']['teamName']
            self._save('player', player)

            recent_matches = data['recentMatches']
            for key in recent_matches.keys():
                if key in leagues_availables:
                    matches = recent_matches[key]
                    
                    for match in matches:
                        self._process_match(match)
                        # time.sleep(1)
        # except:
        #     print('error')


    def _process_data_detail(self, data):
        stats = process_stats(data['content']['stats']['stats'])
        local_team_score = data['header']['teams'][0]['score']
        visit_team_score = data['header']['teams'][1]['score']

        local_team_player_list_data = data['content']['lineup']['lineup'][0]['players']
        visit_team_player_list_data = data['content']['lineup']['lineup'][1]['players']

        local_team_atk_1_combination = []
        local_team_atk_over_2_combination = []
        local_team_def_combination = []
        local_team_player_list = []

        visit_team_atk_1_combination = []
        visit_team_atk_over_2_combination = []
        visit_team_def_combination = []
        visit_team_player_list = []

        for player_list_for_role in local_team_player_list_data:
            for player in player_list_for_role:
                local_team_player_list.append(player['id'])

        for player_list_for_role in visit_team_player_list_data:
            for player in player_list_for_role:
                visit_team_player_list.append(player['id'])

        visit_team_player_list.sort()
        local_team_player_list.sort()




        if local_team_score >= 2:
            roles = ['Midfielder', 'Attacker']
            local_team_atk_over_2_combination = self._check_combination(local_team_player_list_data, roles)

        if local_team_score == 1:
            roles = ['Midfielder', 'Attacker']
            local_team_atk_1_combination = self._check_combination(local_team_player_list_data, roles)

        if visit_team_score == 0:
            roles = ['Keeper', 'Defender']
            local_team_def_combination = self._check_combination(local_team_player_list_data, roles)

        if visit_team_score >= 2:
            roles = ['Midfielder', 'Attacker']
            visit_team_atk_over_2_combination = self._check_combination(visit_team_player_list_data, roles)

        if visit_team_score == 1:
            roles = ['Midfielder', 'Attacker']
            visit_team_atk_1_combination = self._check_combination(visit_team_player_list_data, roles)
        
        if local_team_score == 0:
            roles = ['Keeper', 'Defender']
            visit_team_def_combination = self._check_combination(visit_team_player_list_data, roles)
        



        local_squad = data['content']['lineup']['lineup'][0]
        visit_squad = data['content']['lineup']['lineup'][1]

        local_team_rating = data['content']['lineup']['teamRatings']['home']['num']
        visit_team_rating = data['content']['lineup']['teamRatings']['away']['num']

        top_stats        = stats['top_stats']
        shots_stats      = stats['shots']
        passes_stats     = stats['passes']
        def_stats        = stats['defence']
        duels_stats      = stats['duels']
        discipline_stats = stats['discipline']

        local_team_posession = top_stats['ball_possession'][0]
        visit_team_posession = top_stats['ball_possession'][1]

        local_team_total_shots = shots_stats['total_shots'][0]
        visit_team_total_shots = shots_stats['total_shots'][1]
        
        local_team_shots_on_target = shots_stats['shots_on_target'][0]
        visit_team_shots_on_target = shots_stats['shots_on_target'][1]

        local_team_shots_off_target = shots_stats['shots_off_target'][0]
        visit_team_shots_off_target = shots_stats['shots_off_target'][1]

        local_team_blocked_shots = shots_stats['blocked_shots'][0]
        visit_team_blocked_shots = shots_stats['blocked_shots'][1]

        local_team_keeper_saves = def_stats['keeper_saves'][0]
        visit_team_keeper_saves = def_stats['keeper_saves'][1]

        local_team_big_chances = top_stats['big_chances'][0]
        visit_team_big_chances = top_stats['big_chances'][1]

        local_team_big_chances_missed = top_stats['big_chances_missed'][0]
        visit_team_big_chances_missed = top_stats['big_chances_missed'][1]

        local_team_corners = top_stats['corners'][0]
        visit_team_corners = top_stats['corners'][1]

        local_team_passes = passes_stats['passes'][0]
        visit_team_passes = passes_stats['passes'][1]

        local_team_yellow_cards = discipline_stats['yellow_cards'][0]
        visit_team_yellow_cards = discipline_stats['yellow_cards'][1]

        local_team_red_cards = discipline_stats['red_cards'][0]
        visit_team_red_cards = discipline_stats['red_cards'][1]

        match = Match()
        match.id                                = int(data['general']['matchId'])
        match.name                              = data['general']['matchName']
        match.round                             = data['general']['matchRound']
        match.league_id                         = data['general']['parentLeagueId']
        match.league_name                       = data['general']['leagueName']
        match.match_time_utc                    = data['general']['matchTimeUTC']

        match.local_team_id                     = data['general']['homeTeam']['id']
        match.local_team                        = data['general']['homeTeam']['name']
        match.local_team_score                  = local_team_score
        match.local_team_rating                 = local_team_rating
        match.local_team_posession              = local_team_posession
        match.local_team_total_shots            = local_team_total_shots
        match.local_team_shots_on_target        = local_team_shots_on_target
        match.local_team_shots_off_target       = local_team_shots_off_target
        match.local_team_blocked_shots          = local_team_blocked_shots
        match.local_team_keeper_saves           = local_team_keeper_saves
        match.local_team_big_chances            = local_team_big_chances
        match.local_team_big_chances_missed     = local_team_big_chances_missed
        match.local_team_corners                = local_team_corners
        match.local_team_passes                 = local_team_passes
        match.local_team_yellow_cards           = local_team_yellow_cards
        match.local_team_red_cards              = local_team_red_cards
        match.local_team_player_list            = local_team_player_list
        match.local_team_atk_1_combination      = local_team_atk_1_combination
        match.local_team_atk_over_2_combination = local_team_atk_over_2_combination
        match.local_team_def_combination        = local_team_def_combination

        match.visit_team_id                     = data['general']['awayTeam']['id']
        match.visit_team                        = data['general']['awayTeam']['name']
        match.visit_team_rating                 = visit_team_rating
        match.visit_team_score                  = visit_team_score
        match.visit_team_posession              = visit_team_posession
        match.visit_team_total_shots            = visit_team_total_shots
        match.visit_team_blocked_shots          = visit_team_blocked_shots
        match.visit_team_keeper_saves           = visit_team_keeper_saves
        match.visit_team_shots_on_target        = visit_team_shots_on_target
        match.visit_team_shots_off_target       = visit_team_shots_off_target
        match.visit_team_big_chances            = visit_team_big_chances
        match.visit_team_big_chances_missed     = visit_team_big_chances_missed
        match.visit_team_corners                = visit_team_corners
        match.visit_team_passes                 = visit_team_passes
        match.visit_team_yellow_cards           = visit_team_yellow_cards
        match.visit_team_red_cards              = visit_team_red_cards
        match.visit_team_player_list            = visit_team_player_list
        match.visit_team_atk_1_combination      = visit_team_atk_1_combination
        match.visit_team_atk_over_2_combination = visit_team_atk_over_2_combination
        match.visit_team_def_combination        = visit_team_def_combination
        self._save('match', match)


    def _check_combination(self, player_list, roles):
        combination = []

        for arr in player_list:
            for player in arr:
                if 'role' in player.keys():
                    if player['role'] in roles:
                        combination.append(player['id'])
        combination.sort()
        return combination

    def _save(self, collection, data):
        self.connection[collection].insert_one(data.to_dict())


if __name__ == '__main__':
    scrapper = Fotmob('fotmob', __name__)
    scrapper.start()
