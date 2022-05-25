import requests
from .enum import Sport

class Sportradar:
    def __init__(self, filename, name):
        self.name = name
        self.base_url = 'https://stats.fn.sportradar.com'
        self.sport_selected = None


    def fetch_data_by_league(self, league_id):
       pass



    def fetch_leagues_by_country(self, country_id):
        url = f'/sportradar/en/Europe:Berlin/gismo/config_tree_mini/41/0/{self.sport_selected}/{country_id}'
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
            url = f'/sportradar/en/Europe:Berlin/gismo/config_tree_mini/41/0/{self.sport_selected}'
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

    league_list = {}
    for league in realcategories.values():
        league_list[league['name']] = { 'id': league['_id'] }
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
                print("\033[H\033[J", end="")
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
            print("\033[H\033[J", end="")
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
            print("\033[H\033[J", end="")
            print("invalid option!")
            is_checking_country_input = True


    clear_console()
    print('available leagues:')
    for i, league in enumerate(league_list.keys()):
        print(f"{i + 1} - {league}")