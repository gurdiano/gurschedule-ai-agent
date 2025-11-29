from model.models import Task

def create(session, name, duration, icon_id):
    try:
        obj = Task()
        obj.name = name 
        obj.duration = duration
        obj.icon_id = icon_id

        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj
    except Exception as e:
        raise Exception(f'error: {type(e).__name__} failed to create task!')
     

def find(session, id=None, name=None, duration=None):
    try:
        if id:
            return session.query(Task).filter_by(id=id).first()
        if name and duration:
            return session.query(Task).filter_by(name=name, duration=duration).first()
        if name and not duration:
            return session.query(Task).filter_by(name=name).first()
    except Exception as e:
        raise Exception(f'error: {type(e).__name__} failed to read task!')
    