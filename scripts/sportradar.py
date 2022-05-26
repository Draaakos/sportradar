import requests
from .enum import Sport

class Sportradar:
    def __init__(self, filename, name):
        self.name = name
        self.base_url = 'https://stats.fn.sportradar.com'
        self.sport_selected = None


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

        return home_goals_expected + away_goals_expected

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


    clear_console()
    response_team_list = sportradar.fetch_team_list_by_season(season_id)
    if response_team_list['error'] == False:
        team_list_table_data = response_team_list['response']['doc'][0]['data']['tables'][0]['tablerows']

        team_list = []
        for i, team_row in enumerate(team_list_table_data):
            team_list.append({
                'name': team_row['team']['name'],
                'reference': i
            })
        
        team_selected_home = select_menu_team_list(team_list, 'HOME TEAM')
        team_selected_away = select_menu_team_list(team_list, 'AWAY TEAM')

        home_team_data = team_list_table_data[team_selected_home['reference']]
        away_team_data = team_list_table_data[team_selected_away['reference']]

        clear_console()
        print(f'{home_team_data["team"]["name"]} VS {away_team_data["team"]["name"]}')
        expected_goals = round(calculate_over_under_goals(home_team_data, away_team_data), 2)

        if expected_goals >= 3:
            print(f'the spected goals for this game is {round(expected_goals, 2)}')
            print('recommended!!')
        else:
            print(f'is not recommended this game with expected goals: {expected_goals}')
