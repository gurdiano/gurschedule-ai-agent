from model.models import *
from model.config import *
from model.services import DayService
from model.services import PriorityService
from model.services import TaskService
from model.services import SchedulerService
from datetime import time, datetime
from model.dtos.PriorityDTO import PriorityDTO
from model.dtos.DayDTO import DayDTO
from model.dtos.SchedulerDTO import SchedulerDTO

try:
    create_tables()
except Exception as e:
    raise Exception('Error in create tables.')

def load_priorities():
    with get_db() as session:
        priorities = PriorityService.get_all_priorities(session)

        res = []
        for priority in priorities:
            obj = PriorityDTO(
                id= priority.id,
                name= priority.name,
                color= priority.color,
                icon_id= priority.icon_id
            )
            res.append(obj.get_json())
        return res
    
def load_days():
    with get_db() as session:
        days = DayService.get_all_days(session)

        res = []
        for day in days:
            obj = DayDTO(
                id= day.id,
                date= day.date,
            )
            res.append(obj.get_json())
        return res

def load_schedulers():
    with get_db() as session:
        scheds = SchedulerService.get_all_schedulers(session)

        res = []
        for sched in scheds:
            obj = SchedulerDTO(
                id= sched.id,
                hour= sched.hour,
                begin= sched.begin,
                annotation= sched.annotation,
                day_id= sched.day.id,
                priority_id= sched.priority.id,
                task_id= sched.task.id
            )
            res.append(obj.get_json())
        return res

def save_data(data):
    modulos = data['schedules']

    for mod in modulos:
        day_obj = {
            "date": mod['date']
        }
        task_obj = {
            "name": mod['name'],
            "duration": mod['duration']
        }
        day = __save_day(day_obj)
        priority = __save_priority(mod['priority_id'])
        task = __save_task(task_obj)
        sched = __save_scheduler(mod['hour'], mod['annotation'], day, task, priority)
                                                            
        print(f'sched = {sched}')
    return sched

def __save_day(day):
    date = datetime.strptime(day['date'], "%Y-%m-%d").date()

    with get_db() as session: 
        try:
            return DayService.create(session= session, date= date)
        except Exception:
            session.rollback()
            return DayService.find(session= session, date=date)
        
def __save_priority(priority_id):
    with get_db() as session:
        try:
            return PriorityService.find(session=session, id=priority_id)
        except Exception:
            print(f'priority_id: {priority_id} not found!')
        pass

def __save_task(task):
    with get_db() as session:
        try:
            return TaskService.create(
                session= session,
                name= task['name'],
                duration= task['duration'],
                icon_id= 66,
            )
        except Exception as e:
            session.rollback()
            return TaskService.find(
                session=session,
                name= task['name'],
                duration= task['duration']
            )

def __save_scheduler(hour, annotation, day, task, priority):
        begin = time(hour=hour)

        with get_db() as session:
            try:
                scheduler = SchedulerService.find(
                    session=session,
                    hour= hour,
                    day= day
                )

                if not scheduler: 
                    return SchedulerService.create(
                        session=session,
                        hour= hour,
                        begin= begin,
                        annotation= annotation,
                        day= day,
                        priority= priority,
                        task= task
                    )
            except Exception:
                print(f'failed in create task name: {task.name}')
            pass