import os
import json
import time
import requests

def season_team_list(season):
    url = f'https://stats.fn.sportradar.com/sportradar/es/Europe:Berlin/gismo/stats_season_tables/{season}'
    response = requests.get(url).json()
    response_data = response['doc'][0]['data']['tables'][0]
    max_rounds = response_data['maxrounds']
    current_round = response_data['currentround']
    name = response_data['name']

    team_list = []
    for row in response_data['tablerows']:
        team =  row['team']
        team_list.append({
            'name': team['name'],
            'id': team['uid']
        })

    return {
        'team_list': team_list,
        'max_rounds': max_rounds,
        'current_round': current_round,
        'name': name,
        'information': {}
    }


def _process_matches_file(league_name, season, matches_structure):
    if not os.path.exists(f'data/{league_name}'):
        os.mkdir(f'data/{league_name}')

        with open(f'data/{league_name}/{season}.json', 'w') as json_file:
            initial_data = {
                "team_scanned": [],
                "matches_scanned": [],
                "next_matches": [],
                "completed": False,
                "matches": matches_structure
            }

            json_initial_data = json.dumps(initial_data, indent=4)
            json_file.write(json_initial_data)

    with open(f'data/{league_name}/{season}.json') as json_file:
        information = json.load(json_file)

        if information['completed'] is False:
            return information
            


def team_matches_url(season, team_list, league_name, max_rounds):
    interval_fetch_data = 10
    json_information = {}
    matches = {}
    
    for number_round in range(1, int(max_rounds) + 1):
        matches[f'round_{number_round}'] = {}

    file_information = _process_matches_file(league_name, season, matches)

    for team in team_list:
        url = f'https://stats.fn.sportradar.com/sportradar/es/America:Santiago/gismo/stats_season_teampositionhistory/{season}/{team["id"]}'

        with open(f'data/{league_name}/{season}.json') as json_file:
            json_information = json.load(json_file)


            if not team['id'] in json_information['team_scanned']:
                response = requests.get(url).json()
                match_list_for_team = response['doc'][0]['data']['currentseason'][f'{team["id"]}']

                for match_data in match_list_for_team:
                    match = {
                        "id": match_data['matchid'],
                        "round": match_data['round'],
                        "season_id": match_data['seasonid'],
                        "scrapped": False
                    }

                    matches[f"round_{match_data['round']}"][f"{match_data['matchid']}"] = match
                time.sleep(interval_fetch_data)
                json_information['matches'] = matches
                json_information['team_scanned'].append(team['id'])

            json_to_file = json.dumps(json_information, indent=4)
            with open(f'data/{league_name}/{season}.json', 'w') as new_json_file:
                new_json_file.write(json_to_file)
    
    return json_information


def _process_stats_match_timeline(match_id):
    url = f'https://stats.fn.sportradar.com/sportradar/es/America:Montevideo/gismo/stats_match_timeline/{match_id}'
    response = requests.get(url).json()
    events_data = response['doc'][0]['data']['events']

    available_events = [
        'throwin',
        'freekick',
        'corner',
        'shotofftarget',
        'goal_kick',
        'shotontarget',
        'goalkeeper_saved',
        'goal',
        'offside',
        'shotblocked',
        'card'
    ]

    events = {
        'throwin': [],
        'freekick': [],
        'corner': [],
        'shotofftarget': [],
        'goal_kick': [],
        'shotontarget': [],
        'goalkeeper_saved': [],
        'goal': [],
        'offside': [],
        'shotblocked': [],
        'yellow_card': [],
        'red_card': []
    }

    for event in events_data:
        if event['type'] in available_events:
            if event['type'] == 'card':
                event_name = ''
                if event['name'] == 'Tarjeta Roja' or event['name'] == 'Tarjeta Amarilla/Roja':
                    event_name = 'red_card'
                else:
                    event_name = 'yellow_card'

                events[event_name].append({
                    'name': event['name'],
                    'time': event['time'],
                    'team': event['team']
                })
            else:
                events[event['type']].append({
                    'name': event['name'],
                    'time': event['time'],
                    'team': event['team']
                })

    return events

    

# START
def scrapped_match(match):
    if match['scrapped'] == False:
        squads = _process_match_squads(match['id'])

        data = {
            'lineup': _process_stats_match_lineup(match['id']),
            'squads': squads['squads'],
            'details': _process_match_details(match['id']),
            'home': squads['home'],
            'away': squads['away'],
            'resumen': squads['resumen'],
            'extras': _process_stats_match(match['id']),
            'events': _process_stats_match_timeline(match['id'])
        }
        
        return data
    else:
        return match


def _process_stats_match(match_id):
    url = f'https://stats.fn.sportradar.com/sportradar/es/America:Santiago/gismo/stats_match_get/{match_id}'
    response_data = requests.get(url).json()
    data = response_data['doc'][0]['data']
    referee = {
        'name': data['referee'][0]['name'],
        'nationality': data['referee'][0]['nationality']['name']
    }

    weather = {
        'temperature': data['matchweather']['ctemp'],
        'weather': data['matchweather']['weather']['desc'],
        'humidity': data['matchweather']['humidity'],
        'pressure': data['matchweather']['pressure'],
        'mmprecip': data['matchweather']['mmprecip'],
        'kmphwind': data['matchweather']['kmphwind'],
        'winddirection': data['matchweather']['winddir']
    }

    stadium = {
        'name': data['stadium']['name'],  
        'city': data['stadium']['city'],
        'country': data['stadium']['country'],
        'capacity': data['stadium']['capacity']
    }

    return {
        'referee': referee,
        'weather': weather,
        'stadium': stadium,
        'time': data['time']
    }



def _process_stats_match_lineup(match_id):
    url = f'https://stats.fn.sportradar.com/sportradar/es/Europe:Berlin/gismo/stats_match_lineup/{match_id}'
    return {}


def _process_match_squads(match_id):
    url = f'https://stats.fn.sportradar.com/sportradar/es/America:Santiago/gismo/match_squads/{match_id}'
    response_data = requests.get(url).json()
    data = response_data['doc'][0]['data']
    home_data = data['match']['teams']['home']
    away_data = data['match']['teams']['away']

    home = {
        'id': home_data['uid'],
        'name': home_data['name']
    }

    away = {
        'id': away_data['uid'],
        'name': away_data['name']
    }

    home_manager = {}
    try:
        home_manager = {
            'name': data['home']['manager']['name'],
            'nationality': data['home']['manager']['nationality']['name']
        }
    except:
        home_manager = {
            'name': '',
            'nationality': ''
        }

    away_manager = {}
    try:
        away_manager = {
            'name': data['away']['manager']['name'],
            'nationality': data['away']['manager']['nationality']['name']
        }
    except:
        away_manager = {
            'name': '',
            'nationality': ''
        }

    resumen = {
        'home': {
            'formation': data['home']['startinglineup']['formation'],
            'goals_first_time': data['match']['periods']['p1']['home'],
            'goals_second_time': int(data['match']['result']['home']) - data['match']['periods']['p1']['home'],
            'goals_full_time': data['match']['result']['home'],
            'manager': home_manager
        },
        'away': {
            'formation': data['away']['startinglineup']['formation'],
            'goals_first_time': data['match']['periods']['p1']['away'],
            'goals_second_time': int(data['match']['result']['away']) - data['match']['periods']['p1']['away'],
            'goals_full_time': data['match']['result']['away'],
            'manager': away_manager
        }
    }

    return {
        'resumen': resumen,
        'squads': {},
        'home': home,
        'away': away
    }


def _process_match_details(match_id):
    url = f'https://stats.fn.sportradar.com/sportradar/es/America:Santiago/gismo/match_details/{match_id}'
    response_data = requests.get(url).json()
    data = response_data['doc'][0]['data']
    print(f'processing {data["teams"]["home"]} vs {data["teams"]["away"]}')

    key_values = {
        'Posesión de la pelota': 'possesion',
        'Ocasiones de Gol': 'goal_chances',
        'Tiros a portería': 'shots_on_goal',
        'Tiros fuera': 'shots_out',
        'Saques de esquina': 'corners',
        'Faltas': 'faults',
        'Fueras de juego': 'offsides',
        'Saques de puerta': 'goal_kicks',
        'Saques de banda': 'throwins',
        'Tarjetas Amarillas': 'yellow_cards',
        'Tarjetas Rojas': 'red_cards',
        'Paradas': 'goalkeeper_stops'    
    }

    information = {
        'possesion': {
            'home': 0,
            'away': 0
        },
        'goal_chances': {
            'home': 0,
            'away': 0
        },
        'shots_on_goal': {
            'home': 0,
            'away': 0
        },
        'shots_out': {
            'home': 0,
            'away': 0
        },
        'corners': {
            'home': 0,
            'away': 0
        },
        'faults': {
            'home': 0,
            'away': 0
        },
        'offsides': {
            'home': 0,
            'away': 0
        },
        'goal_kicks': {
            'home': 0,
            'away': 0
        },
        'throwins': {
            'home': 0,
            'away': 0
        },
        'yellow_cards': {
            'home': 0,
            'away': 0
        },
        'red_cards': {
            'home': 0,
            'away': 0
        },
        'goalkeeper_stops': {
            'home': 0,
            'away': 0
        },
    }

    for item in data['values'].values():
        if item['name'] in key_values.keys():
            information[key_values[item['name']]] = {
                'home': item['value']['home'],
                'away': item['value']['away']
            }

    return information



def update_next_matches(matches_finished, season):
    url = f'https://stats.fn.sportradar.com/sportradar/es/America:Santiago/gismo/stats_season_fixtures2/{season}'
    response = requests.get(url).json()
    matches = response['doc'][0]['data']['matches']

    next_matches = []
    for match in matches:
        match_id = match['_id']

        if not match_id in matches_finished:
            next_matches.append({
                'match': match_id,
                'round': match['round'],
                'home': match['teams']['home']['uid'],
                'away': match['teams']['away']['uid'],
                'time': match['time'],
                'finished': True if match['result']['home'] is not None and match['result']['away'] is not None else False
            })

    return next_matches
