class MatchNextRound:
    def __init__(self):
        self.id = None
        self.round = None
        self.local_team = None
        self.visit_team = None
        self.date = None


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
                'round': self.round,
                'local_team': self.local_team,
                'visit_team': self.visit_team,
                'date': self.date
            }
        }