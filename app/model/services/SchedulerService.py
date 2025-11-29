from model.models import Scheduler

def get_all_schedulers(session):
    try:
        return session.query(Scheduler).all()
    except Exception as e:
        return Exception('error: failed to get_all_schedulers()')

def create(session, hour, begin, day, priority, task, annotation=None):
    try:
        obj = Scheduler()
        obj.hour = hour
        obj.begin = begin
        obj.annotation = annotation
        obj.day_id = day.id
        obj.priority_id = priority.id
        obj.task_id = task.id

        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj
    except Exception as e:
        raise Exception(f'SchedulerService.create() failed to create scheduling! msg:{e}')
    
def find(session, id=None, hour=None, day=None, task=None):
    try:
        if id:
            return session.query(Scheduler).filter_by(id=id).first()
        if hour and day and task:
            return session.query(Scheduler).filter_by(hour=hour, day_id=day.id, task_id=task.id).first()
        if hour and day:
            return session.query(Scheduler).filter_by(hour=hour, day_id=day.id).first()
    except Exception as e:
        raise Exception(f'error: {type(e).__name__} Could not read the schedule. Please enter the ID or the hour, day, and task to proceed.')