class Reform:
    def __init__(self, reform_data):
        self.type = reform_data['tipo'].strip()
        self.year = reform_data['fecha'].strip()
        pass

    def to_json(self):
        return dict(type=self.type, year=self.year)