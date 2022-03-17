class Match:
    def __init__(self):
        self.id = None
        self.name = None
        self.round = None
        self.league_id = None
        self.league_name = None
        self.match_time_utc = None

        self.local_team_id = None
        self.local_team = None
        self.local_team_rating = None
        self.local_team_score = None
        self.local_team_posession = None
        self.local_team_total_shots = None
        self.local_team_shots_on_target = None
        self.local_team_shots_off_target = None
        self.local_team_blocked_shots = None
        self.local_team_keeper_saves = None
        self.local_team_big_chances = None
        self.local_team_big_chances_missed = None
        self.local_team_corners = None
        self.local_team_passes = None
        self.local_team_yellow_cards = None
        self.local_team_red_cards = None
        self.local_team_player_list = None
        self.local_team_atk_1_combination = None
        self.local_team_atk_over_2_combination = None
        self.local_team_def_combination = None

        self.visit_team_id = None
        self.visit_team = None
        self.visit_team_rating = None
        self.visit_team_score = None
        self.visit_team_posession = None
        self.visit_team_total_shots = None
        self.visit_team_shots_on_target = None
        self.visit_team_shots_off_target = None
        self.visit_team_blocked_shots = None
        self.visit_team_keeper_saves = None
        self.visit_team_big_chances = None
        self.visit_team_big_chances_missed = None
        self.visit_team_corners = None
        self.visit_team_passes = None
        self.visit_team_yellow_cards = None
        self.visit_team_red_cards = None
        self.visit_team_player_list = None
        self.visit_team_atk_1_combination = None
        self.visit_team_atk_over_2_combination = None
        self.visit_team_def_combination = None


    def _is_valid(self):
        fields = [field for field in vars(self) if not field.startswith('_')]
        self._errors = []

        for key in fields:
            if getattr(self, key) is None:
                self._errors.append(key)

        return len(self._errors) == 0

    def to_dict(self):
        if not self._is_valid():
            errors = ','.join(self._errors)
            message = f'These fields are not completed yet {errors}'
            raise TypeError(message)

        return {
            'information': {
                'id': self.id,
                'name': self.name,
                'round': self.round,
                'time_utc': self.match_time_utc,
                'league': {
                    'id': self.league_id,
                    'name': self.league_name
                },
                'home': {
                    'id': self.local_team_id,
                    'name': self.local_team,
                    'rate': self.local_team_rating,
                    'score': self.local_team_score,
                    'player_list': self.local_team_player_list,
                    'stats': {
                        'possesion': self.local_team_posession,
                        'total_shots': self.local_team_total_shots,
                        'shots_on_target': self.local_team_shots_on_target,
                        'shots_off_target': self.local_team_shots_off_target,
                        'blocked_shots': self.local_team_blocked_shots,
                        'keeper_saves': self.local_team_keeper_saves,
                        'big_chances': self.local_team_big_chances,
                        'big_chances_missed': self.local_team_big_chances_missed,
                        'corners': self.local_team_corners,
                        'passes': self.local_team_passes,
                        'yellow': self.local_team_yellow_cards,
                        'red': self.local_team_red_cards
                    },
                    'combinations': {
                        'atk_1': self.local_team_atk_1_combination,
                        'atk_over_2': self.local_team_atk_over_2_combination,
                        'def': self.local_team_def_combination
                    }
                },
                'away': {
                    'id': self.visit_team_id,
                    'name': self.visit_team,
                    'rate': self.visit_team_rating,
                    'score': self.visit_team_score,
                    'player_list': self.visit_team_player_list,
                    'stats': {
                        'possesion': self.visit_team_posession,
                        'total_shots': self.visit_team_total_shots,
                        'shots_on_target': self.visit_team_shots_on_target,
                        'shots_off_target': self.visit_team_shots_off_target,
                        'blocked_shots': self.visit_team_blocked_shots,
                        'keeper_saves': self.visit_team_keeper_saves,
                        'big_chances': self.visit_team_big_chances,
                        'big_chances_missed': self.visit_team_big_chances_missed,
                        'corners': self.visit_team_corners,
                        'passes': self.visit_team_passes,
                        'yellow': self.visit_team_yellow_cards,
                        'red': self.visit_team_red_cards
                    },
                    'combinations': {
                        'atk_1': self.visit_team_atk_1_combination,
                        'atk_over_2': self.visit_team_atk_over_2_combination,
                        'def': self.visit_team_def_combination
                    }
                }
            }
        }
