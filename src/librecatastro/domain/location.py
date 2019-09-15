class Location:
    def __init__(self, longitude, latitude):
        self.lon = longitude
        self.lat = latitude

    def to_json(self):
        return "{'location': {'lon': {}, 'lat': {}}".format(float(self.lon) if self.lon is not None else None,
                                                            float(self.lat) if self.lat is not None else None)
