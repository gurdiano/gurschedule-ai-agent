from model.models import Priority

def get_all_priorities(session):
    try:
        return session.query(Priority).all()
    except Exception as e:
        return Exception('error: failed to get_all_priorities()')
    
def find(session, id=None, name=None, color=None):
    try:
        if id:
            return session.query(Priority).filter_by(id=id).first()
        if name:
            return session.query(Priority).filter_by(name=name).first()
        if color:
            return session.query(Priority).filter_by(color=color).first()
    except Exception as e:
        raise Exception(f'error: {type(e).__name__} failed to read a Priority!')