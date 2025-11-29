class PriorityDTO:
    def __init__(self, id, name, color, icon_id):
        self.id = id
        self.name = name
        self.color = color
        self.icon_id = icon_id
        pass

    def get_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "color": self.color,
            "icon_id": self.icon_id,
        }