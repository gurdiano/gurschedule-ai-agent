from model.models import Day

def get_all_days(session):
    try:
        return session.query(Day).all()
    except Exception as e:
        return Exception('error: failed to get_all_days()')
    
def create(session, date):
    try:
        obj = Day(date=date)

        session.add(obj)
        session.commit()
        session.refresh(obj)

        return obj
    except Exception as e:
        raise Exception(f'failed to create a day! error: {type(e).__name__}')

def find(session, id=None, date=None):
    try:
        if id:
            return session.query(Day).filter_by(id=id).first()
        if date:
            return session.query(Day).filter_by(date=date).first()
    except Exception as e:
        raise Exception(f'failed to read a day! error: {id}{date} ,{type(e).__name__}')