import os
import json
import time
import requests


def season_data(country, league_name, season):
    url = f'https://stats.fn.sportradar.com/sportradar/es/America:Santiago/gismo/stats_season_fixtures2/{season}'
    print('fetching data...', url)

    response = requests.get(url).json()
    # league_name = response['doc'][0]['data']['name']

    teams = []
    teams_scanned = []

    matches = {}

    response_matches = response['doc'][0]['data']['matches']
    for match in response_matches:
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
            'season': int(season),
            'match': int(match['_id']),
            'round': int(match['round']),
            'home': int(match['teams']['home']['uid']),
            'away': int(match['teams']['away']['uid']),
            'time': match['time'],
            'finished': True if match['result']['home'] is not None and match['result']['away'] is not None else False,
            'data': {},
            'previous': {
                "match": -1,
                "goal_1t": -1,
                "goal_2t": -1,
                "goal_ft": -1
            }
        }

    # esta seria la etapa 1 del archivo donde se crea 
    # la base y si ya existe, se recupera el archivo
    base_file_data = _process_base_file(country, league_name, season, teams, matches)

    ready_for_scan = []
    for match in response_matches:
        finished = True if match['result']['home'] is not None and match['result']['away'] is not None else False

        if not int(match['_id']) in base_file_data['matches_scanned'] and finished == True:
            ready_for_scan.append(int(match['_id']))

    _scrapped_matches(country, league_name, season, base_file_data, ready_for_scan)

  

def _process_base_file(country, league_name, season, teams, matches):
    if not os.path.exists(f'data/{country}'):
        os.mkdir(f'data/{country}')

    if not os.path.exists(f'data/{country}/{league_name}'):
        os.mkdir(f'data/{country}/{league_name}')

        with open(f'data/{country}/{league_name}/{season}.json', 'w') as json_file:
            initial_data = {
                "teams": teams,
                "matches": matches,
                "matches_scanned": []
            }

            json_initial_data = json.dumps(initial_data, indent=4)
            json_file.write(json_initial_data)

            return initial_data

    else:
        with open(f'data/{country}/{league_name}/{season}.json') as json_file:
            return json.load(json_file)





def _scrapped_matches(country, league_name, season, base_file_data, ready_for_scan):
    for match_id in base_file_data['matches'].keys():
        if not int(match_id) in base_file_data['matches_scanned'] and base_file_data['matches'][match_id]['finished'] == True or int(match_id) in ready_for_scan:
            print(f'processing... {match_id}')
            squads = _process_match_squads(match_id)

            data = {
                'home': squads['home'],
                'away': squads['away'],
                'events': _process_stats_match_timeline(match_id)
            }

            previous = _fetch_previous_game(int(data['home']['uid']), int(data['away']['uid']), base_file_data['matches'][match_id]['time'])

            base_file_data['matches'][match_id]['data'] = data
            base_file_data['matches'][match_id]['finished'] = True
            base_file_data['matches_scanned'].append(int(match_id))
            base_file_data['matches'][match_id]['previous'] = previous

            json_to_file = json.dumps(base_file_data, indent=4)
            with open(f'data/{country}/{league_name}/{season}.json', 'w') as new_json_file:
                new_json_file.write(json_to_file)

            time.sleep(10)

            




def _process_match_squads(match_id):
    url = f'https://stats.fn.sportradar.com/sportradar/es/America:Santiago/gismo/match_squads/{match_id}'
    response_data = requests.get(url).json()
    print(f'fetching match... {url}')

    data = response_data['doc'][0]['data']
    home = data['match']['teams']['home']
    away = data['match']['teams']['away']

    return {
        'home': home,
        'away': away
    }







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




def _fetch_previous_game(team_a, team_b, match_time):
    last_match = {
        'match': None,
        'goal_1t': 0,
        'goal_2t': 0,
        'goal_ft': 0
    }
    
    try:
        teams = sorted([team_a, team_b])
        url = f'https://stats.fn.sportradar.com/sportradar/es/America:Santiago/gismo/stats_h2h_versus/{teams[0]}/{teams[1]}'
        response = requests.get(url).json()
        lastmatchesbetweenteams = response['doc'][0]['data']['lastmatchesbetweenteams']

        first_coincidence = False
        current_match_time = int(match_time['uts'])
        for match in lastmatchesbetweenteams:
            if first_coincidence == False and int(match['time']['uts']) < current_match_time:
                goal_1t = int(match['periods']['p1']['home']) + int(match['periods']['p1']['away'])
                goal_ft = int(match['periods']['ft']['home']) + int(match['periods']['ft']['away'])

                last_match = {
                    'match': int(match['_id']),
                    'goal_1t': goal_1t,
                    'goal_2t': goal_ft - goal_1t,
                    'goal_ft': goal_ft
                }

                first_coincidence = True
    except:
        print('execption previous game')
   

    return last_match