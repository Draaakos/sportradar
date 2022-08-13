import time
import requests
import datetime
from .enum import Sport


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    IMPORTANT = '\33[42m'


class Sportradar:
    def __init__(self, filename, name):
        self.name = name
        self.base_url = 'https://stats.fn.sportradar.com'
        self.sport_selected = None


    def fetch_matches_by_season(self, season_id):
        url = f'sportradar/en/America:Montevideo/gismo/stats_season_fixtures2/{season_id}/1'
        print(f'{self.base_url}/{url}')
        try:
            response = requests.get(f'{self.base_url}/{url}').json()
            return {
                "error": False,
                "response": response,
            }
        except:
            return {
                "error": True,
                "response": {},
                "reason": "response"
            }


    def fetch_team_list_by_season(self, season_id):
        url = f'sportradar/en/Europe:Berlin/gismo/stats_season_tables/{season_id}'
        try:
            response = requests.get(f'{self.base_url}/{url}').json()
            return {
                "error": False,
                "response": response,
            }
        except:
            return {
                "error": True,
                "response": {},
                "reason": "response"
            }
            



    def fetch_leagues_by_country(self, country_id):
        url = f'sportradar/en/Europe:Berlin/gismo/config_tree_mini/41/0/{self.sport_selected}/{country_id}'
        try:
            response = requests.get(f'{self.base_url}/{url}').json()
            return {
                "error": False,
                "response": response,
            }
        except:
            return {
                "error": True,
                "response": {},
                "reason": "response"
            }


    def fetch_region_by_sport(self, sport_name):
        try:
            self.sport_selected = Sport[sport_name.upper()].value
        except:  
            return {
                "error": True,
                "response": {},
                "reason": "invalid_option"
            }

        try:
            url = f'sportradar/en/Europe:Berlin/gismo/config_tree_mini/41/0/{self.sport_selected}'
            response = requests.get(f"{self.base_url}/{url}").json()
            return {
                "error": False,
                "response": response,
            }
        except:
            return {
                "error": True,
                "response": {},
                "reason": "response"
            }


def process_region_response(response):
    realcategories = response['response']['doc'][0]['data'][0]['realcategories']

    region_list = {}
    for category in realcategories:
        if category.get('cc') is not None:
            cc = category['cc']
            
            if cc.get('continent') is not None:
                continent = cc['continent']

                try:
                    region_list[continent.lower()][category['name'].lower()] = { 'id': category['_id'] }
                except KeyError:
                    region_list[continent.lower()] = {}
                    region_list[continent.lower()][category['name'].lower()] = { 'id': category['_id'] }
    return region_list


def process_leagues_response(response):
    realcategories = response['response']['doc'][0]['data'][0]['realcategories'][0]['uniquetournaments']
    # realcategories = response['response']['doc'][0]['data'][0]['realcategories'][0]['tournaments']

    league_list = []
    for i, key in enumerate(realcategories.keys()):
        league_list.append({ 
            'name': realcategories[key]['name'], 
            'season_id': realcategories[key]['currentseason'], 
            'option': i 
        })
        print(realcategories[key]['name'])
    return league_list


def clear_console():
    print("\033[H\033[J", end="")
    # pass


if __name__ == '__main__':
    sportradar = Sportradar('sportradar', __name__)

    region_list = []
    is_checking_sport_input = True
    while is_checking_sport_input:
        sport_input = input("sport name: ")
        
        response_sport_region_by_sport = sportradar.fetch_region_by_sport(sport_input)
        if response_sport_region_by_sport['error'] == True:
            if response_sport_region_by_sport['reason'] == 'invalid_option':
                clear_console()
                print("invalid option!")
            elif response_sport_region_by_sport['reason'] == 'response':
                print('fetchdata error')
                break

        if response_sport_region_by_sport['error'] == False:
            region_list = process_region_response(response_sport_region_by_sport)
            is_checking_sport_input = False
    
    clear_console()
    country_list = []
    is_checking_continent_input = True
    while is_checking_continent_input:
        print('available options:')
        for option in region_list.keys():
            print(option)
        print('**************************************')
        country_input = input("insert continent name: ")

        if country_input.lower() in region_list:
            country_list = region_list[country_input.lower()]
            is_checking_continent_input = False
        else:
            is_checking_continent_input = True
            clear_console()
            print("invalid option!")


    clear_console()
    league_list = []
    is_checking_country_input = True
    while is_checking_country_input:
        country_available_option_list = []
        for option in country_list.keys():
            country_available_option_list.append(option)

        print('available options:')
        print(country_available_option_list)
        print('**************************************')
        country_input = input("insert country name: ")

        if country_list.get(country_input.lower()) is not None:
            country_id_selected = country_list[country_input.lower()]['id']
            is_checking_country_input = False

            try:
                response_leagues_by_country = sportradar.fetch_leagues_by_country(country_id_selected)
                league_list = process_leagues_response(response_leagues_by_country)
            except:
                clear_console()
                print('request error or processing region response function')
        else:
            clear_console()
            print("invalid option!")
            is_checking_country_input = True


    clear_console()
    print('available leagues:')
    is_checking_league_input = True
    season_id = None
    while is_checking_league_input:
        for i, item in enumerate(league_list):
            print(f"{i + 1} - {item['name']}")
        
        try:
            option_number = -1
            option_number = int(input('select an option number: '))
            for item in league_list:
                if item['option'] == option_number - 1:
                    season_id = item['season_id']
                    is_checking_league_input = False
        except:
            print('invalid option')


    def calculate_over_under_goals(home_team, away_team):
        # HOME --------------------------------------------
        home_total_games_played = home_team['total']
        home_total_goals = home_team['goalsForTotal']
        home_games_played = home_team['home']
        home_goals = home_team['goalsForHome']
        home_goals_against_home = home_team['goalsAgainstHome']

        # AWAY --------------------------------------------
        away_total_games_played = away_team['total']
        away_total_goals = away_team['goalsForTotal']
        away_games_played_away = away_team['away']
        away_goals_away = away_team['goalsForAway']
        away_goals_against_away = away_team['goalsAgainstAway']

        # HOME AVERAGES
        home_goals_average = home_goals / home_games_played
        home_goals_against_home_average = home_goals_against_home / home_games_played
        home_league_goals_average = home_total_goals / home_total_games_played

        # AWAY AVERAGES
        away_goals_average = away_goals_away / away_games_played_away
        away_goals_against_away_average = away_goals_against_away / away_games_played_away
        away_league_goals_average = away_total_goals / away_total_games_played


        home_team_nivel_atk = home_goals_average / home_league_goals_average
        away_team_nivel_def = away_goals_against_away_average / home_league_goals_average
        home_goals_expected = home_team_nivel_atk * away_team_nivel_def * home_league_goals_average

        away_team_nivel_atk = away_goals_average / away_league_goals_average
        away_team_nivel_def = home_goals_against_home_average / away_league_goals_average
        away_goals_expected = away_team_nivel_atk * away_team_nivel_def * away_league_goals_average

        return {
            'expected_goals': round(home_goals_expected + away_goals_expected, 1),
            'home_goals_expected': round(home_goals_expected, 1),
            'away_goals_expected': round(away_goals_expected, 1)
        }

        # print('equipos locales', home_league_goals_average)
        # print('equipos visitantes', away_league_goals_average)

        # print('PROMEDIO ANOTADO LOCAL', home_goals_average)
        # print('PROMEDIO RECIBIDO LOCAL', home_goals_against_home_average)

        # print('PROMEDIO ANOTADO VISITA', away_goals_average)
        # print('PROMEDIO RECIBIDO VISITA', away_goals_against_away_average)

        # print('FUERZA ATACANTE EQUIPO 1', home_team_nivel_atk)
        # print('FUERZA DEFENSIVA  EQUIPO 2', away_team_nivel_def)
        # print('GOLES ESPERADOS', home_goals_expected)

        # print('FUERZA ATACANTE EQUIPO 2', away_team_nivel_atk)
        # print('FUERZA DEFENSIVA EQUIPO 1', away_team_nivel_def)
        # print('GOLES ESPERADOS EQUIPO VISITANTE', away_goals_expected)



    def select_menu_team_list(team_list, textTeam):
        clear_console()
        is_option_invalid = True
        reference_selected = -1
        while is_option_invalid:
            for team in team_list:
                print(f'{team["reference"] + 1}: {team["name"]}')
            try:
                print('**************************************')
                option = int(input(f'Select a number for {textTeam}: '))
                reference_selected = team_list[option - 1]
                is_option_invalid = False
            except:
                print("invalid option, try again")
        return reference_selected





    # FETCH TEAM LIST AND SEASON INFORMATION
    team_list = {}
    team_list_table_data = []
    current_round = None
    response_team_list = sportradar.fetch_team_list_by_season(season_id)
    if response_team_list['error'] == False:
        current_round = int(response_team_list['response']['doc'][0]['data']['tables'][0]['currentround'])
        team_list_table_data = response_team_list['response']['doc'][0]['data']['tables'][0]['tablerows']

        for i, team_row in enumerate(team_list_table_data):
            team_list[team_row['team']['_id']] = {
                'name': team_row['team']['name'], 
                'reference': i
            }


    print(current_round)
    match_list_by_season = sportradar.fetch_matches_by_season(season_id)
    # print('match_list_by_season', match_list_by_season)
    if match_list_by_season['error'] == False:
        matches = match_list_by_season['response']['doc'][0]['data']['matches']


        # for match in matches:
        #     if match['round']







        
        now = datetime.datetime.now()
        # current_round = 1000
        next_matches = []
        for match in matches:
            match_home_result = match['result']['home']
            match_away_result = match['result']['away']
            
            match_time_splitted = match['time']['date'].split('/')
            match_time_day = int(match_time_splitted[0])
            match_time_month = int(match_time_splitted[1])
            match_time_year = int(f'20{match_time_splitted[2]}')
            match_time = datetime.date(match_time_year, match_time_month, match_time_day)

            if int(match['round']) == current_round or int(match['round']) == current_round + 1:
                next_matches.append(match)


            # if (match['result']['home'] == None and match['result']['away'] == None):

            #     if current_round > int(match['round']):
            #         current_round = int(match['round'])
                
            #     if int(match['round']) == current_round or (current_round + 1) == int(match['round']):
            #         next_matches.append(match)

                    
        
        clear_console()
        print(f'THE NEXT MATCHES FOR ROUND {current_round} ARE:')
        print('***********************************************')

        for match in next_matches:
            match_time = match['time']['date']
            home_team_data_position = team_list[match['teams']['home']['_id']]['reference']
            home_team_data = team_list_table_data[home_team_data_position]

            away_team_data_position = team_list[match['teams']['away']['_id']]['reference']
            away_team_data = team_list_table_data[away_team_data_position]

            home_team_name = match['teams']['home']['name']
            away_team_name = match['teams']['away']['name']

            try:

                expected_goals_calculate = calculate_over_under_goals(home_team_data, away_team_data)
                expected_goals = expected_goals_calculate['expected_goals']
                expected_goals_home = expected_goals_calculate['home_goals_expected']
                expected_goals_away = expected_goals_calculate['away_goals_expected']

                print(bcolors.WARNING + f"ROUND {match['round']}" + bcolors.ENDC)
                print(f'NAME: {home_team_name} VS {away_team_name}')
                print(f'DATE: ' + bcolors.OKCYAN + f"{match_time}" + bcolors.ENDC)
                print(f'SPECTED_GOALS: {expected_goals}')
                print(f'SPECTED_GOALS_HOME: {expected_goals_home}')
                print(f'SPECTED_GOALS_AWAY: {expected_goals_away}')

                if expected_goals >= 3:
                    if expected_goals >= 4:
                        print(bcolors.IMPORTANT + "RECOMMENDED +2 OR +2.5 GOALS IN THE GAME" + bcolors.ENDC)
                    else:
                        print(bcolors.OKGREEN + "RECOMMENDED +2 GOALS IN THE GAME" + bcolors.ENDC)
                elif expected_goals <= 1.5:
                    if expected_goals <= 1:
                        print(bcolors.IMPORTANT + "RECOMMENDED -2.5 OR -3 GOALS IN THE GAME" + bcolors.ENDC)
                    else:
                        print(bcolors.OKGREEN + "RECOMMENDED -3 GOALS IN THE GAME" + bcolors.ENDC)
                else:
                    print(bcolors.FAIL + "NOT RECOMMENDED" + bcolors.ENDC)
                print('***********************************************')
            except:
                print('error')
            
            





    # clear_console()
    # response_team_list = sportradar.fetch_team_list_by_season(season_id)
    # if response_team_list['error'] == False:
    #     team_list_table_data = response_team_list['response']['doc'][0]['data']['tables'][0]['tablerows']

    #     team_list = []
    #     for i, team_row in enumerate(team_list_table_data):
    #         team_list.append({
    #             'name': team_row['team']['name'],
    #             'reference': i
    #         })
        
    #     team_selected_home = select_menu_team_list(team_list, 'HOME TEAM')
    #     team_selected_away = select_menu_team_list(team_list, 'AWAY TEAM')

    #     home_team_data = team_list_table_data[team_selected_home['reference']]
    #     away_team_data = team_list_table_data[team_selected_away['reference']]

    #     clear_console()
    #     print(f'{home_team_data["team"]["name"]} VS {away_team_data["team"]["name"]}')
    #     expected_goals = round(calculate_over_under_goals(home_team_data, away_team_data), 2)

    #     if expected_goals >= 3:
    #         print(f'the spected goals for this game is {round(expected_goals, 2)}')
    #         print('recommended!!')
    #     else:
    #         print(f'is not recommended this game with expected goals: {expected_goals}')
