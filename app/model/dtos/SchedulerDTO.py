class SchedulerDTO:
    def __init__(self, id, hour, begin, annotation, day_id, task_id, priority_id):
        self.id = id
        self.hour = hour
        self.begin = begin
        self.annotation = annotation
        self.day_id = day_id
        self.task_id = task_id
        self.priority_id = priority_id
        pass

    def get_json(self):
        return {
            "id": self.id,
            "hour": self.hour,
            "begin": self.begin,
            "annotation": self.annotation,
            "day_id": self.day_id,
            "task_id": self.task_id,
            "priority_id": self.priority_id,
        }