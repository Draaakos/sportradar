class Player:
    def __init__(self):
        self.id = None
        self.name = None
        self.team_id = None
        self.team_name = None


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
                'team_id': self.team_id,
                'team_name': self.team_name
            }
        }
