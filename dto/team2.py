class Team:
    def __init__(self):
        self.id = None
        self.name = None
        self.name_data = None
        self.url = None
        self.played = None
        self.wins = None
        self.draws = None
        self.losses = None
        self.points = None
        self.position = None


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
                'name_data': self.name_data,
                'url': self.url,
                'played': self.played,
                'wins': self.wins,
                'draws': self.draws,
                'losses': self.losses,
                'points': self.points,
                'position': self.position
            }
        }
