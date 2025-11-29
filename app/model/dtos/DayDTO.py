class DayDTO:
    def __init__(self, id, date):
        self.id = id
        self.date = date
        pass

    def get_json(self):
        return {
            "id": self.id,
            "date": self.date,
        }