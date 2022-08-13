import os
import json
import time
import requests

def season_data(season):
    url = f'https://stats.fn.sportradar.com/sportradar/es/America:Santiago/gismo/stats_season_fixtures2/{season}'
    response = requests.get(url).json()
    league_name = response['doc'][0]['data']['name']

    teams = []
    teams_scanned = []

    matches = {}

    for match in response['doc'][0]['data']['matches']:
        if not match['teams']['home']['uid'] in teams_scanned:
            teams.append({
                'id': match['teams']['home']['uid'],
                'name': match['teams']['home']['name'],
                'medium_name': match['teams']['home']['mediumname'],
                'abbr': match['teams']['home']['abbr']
            })
            teams_scanned.append(match['teams']['home']['uid'])

        if not match['teams']['away']['uid'] in teams_scanned:
            teams.append({
                'id': match['teams']['away']['uid'],
                'name': match['teams']['away']['name'],
                'medium_name': match['teams']['away']['mediumname'],
                'abbr': match['teams']['away']['abbr']
            })
            teams_scanned.append(match['teams']['away']['uid'])
            

        # informacion este o no este el partido terminado.
        # esto es para armar la temporada completa
        matches[match['_id']] = {
            'season': season,
            'match': match['_id'],
            'round': match['round'],
            'home': match['teams']['home']['uid'],
            'away': match['teams']['away']['uid'],
            'time': match['time'],
            'finished': True if match['result']['home'] is not None and match['result']['away'] is not None else False,
            'data': {}
        }

    # esta seria la etapa 1 del archivo donde se crea 
    # la base y si ya existe, se recupera el archivo
    base_file_data = _process_base_file(league_name, season, teams, matches)
    _scrapped_matches(league_name, season, base_file_data)

    return league_name

  

def _process_base_file(league_name, season, teams, matches):
    if not os.path.exists(f'data/{league_name}'):
        os.mkdir(f'data/{league_name}')

        with open(f'data/{league_name}/{season}.json', 'w') as json_file:
            initial_data = {
                "teams": teams,
                "matches": matches,
                "matches_scanned": []
            }

            json_initial_data = json.dumps(initial_data, indent=4)
            json_file.write(json_initial_data)

            return initial_data

    else:
        with open(f'data/{league_name}/{season}.json') as json_file:
            return json.load(json_file)





def _scrapped_matches(league_name, season, base_file_data):
    for match_id in base_file_data['matches'].keys():
        if not match_id in base_file_data['matches_scanned'] and base_file_data['matches'][match_id]['finished'] == True:
            squads = _process_match_squads(match_id)

            data = {
                'squads': squads['squads'],
                'home': squads['home'],
                'away': squads['away'],
                'resumen': squads['resumen'],
                'details': _process_match_details(match_id),
                'extras': _process_stats_match(match_id),
                'events': _process_stats_match_timeline(match_id)
            }

            base_file_data['matches'][match_id]['data'] = data
            base_file_data['matches_scanned'].append(match_id)

            json_to_file = json.dumps(base_file_data, indent=4)
            with open(f'data/{league_name}/{season}.json', 'w') as new_json_file:
                new_json_file.write(json_to_file)

            time.sleep(10)

            




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

    players = {}

    return {
        'resumen': resumen,
        'squads': players,
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