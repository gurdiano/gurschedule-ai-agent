import os
from google import genai
from google.genai import types
from model import init_db
from exceptions import ModelGenerationError
from dotenv import load_dotenv

load_dotenv()
GEMINI_KEY = os.getenv('GEMINI_API_KEY')
OPEN_TIME = os.getenv('OPEN_TIME')
CLOSE_TIME = os.getenv('CLOSE_TIME')
DURATION = os.getenv('DURATION')
DAILY_LIMIT = os.getenv('DAILY_LIMIT')

# Requesting to AI API...
def request_AI_response(config, prompt, retry_count=0):
    # Configure the client
    client = genai.Client(api_key=GEMINI_KEY)
    retry = 5

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=config,
        )

        if response.candidates[0].content.parts[0].function_call:
            function_call = response.candidates[0].content.parts[0].function_call
            print(f"\nFunction to call: {function_call.name}")
            print(f"Arguments: {function_call.args}")

            return function_call.args
        else:
            print("The model returned text instead of a function_call.", response.text)
            return response.text

    except AttributeError as e:  
        if retry_count < retry:
            print(f"Attribute not found. Retrying... ({retry_count + 1}/{retry})")
            return request_AI_response(config, prompt, retry_count + 1)
        else:
            raise ModelGenerationError(retry_count)

# 1.
# Free time definition
def time_definition(date):
    # Define personal Schemas 
    freetime_schema = {
        "type": "object",
        "properties": {
            "day": {
                "type": "string",
                "description": "Day when available (e.g., 'yyyy-mm-dd')."
            },
            "hours": {
                "type": "array",
                "items": {
                    "type": "integer",
                    "description": "Hour available from 0 to 23."
                }
            }
        }
    }

    # Define the function declaration for the model
    set_freetime_function = {
        "name": "set_freetime",
        "description": "Analyzes which hours of a given day are free based on the provided schedule data.",
        "parameters": {
            "type": "object",
            "properties": {
                "freetime": {
                    "type": "array",
                    "items": freetime_schema
                },
                "totaltime": {
                    "type": "integer",
                    "description": "Total hours available."
                } 
            },
            "required": ["freetime", "totaltime"]
        },
    }

    # Load Days from database
    days = init_db.load_days()
    prompt_days = f"""
    List of existing base days.".

    Days list:
    {days}

    """

    # Load Schedulers from database
    schedulers = init_db.load_schedulers()
    prompt_schedulers = f"""
    List of already scheduled tasks for the base."

    List of schedules:
    {schedulers}

    """

    # PROMPT 
    prompt_base = f"""
    The user will provide a date".

    Your task is:
    1. Generate daily study time slots between {OPEN_TIME} and {CLOSE_TIME}.
    2. Consider 'available times' as those not present in the existing schedule list.
    3. Duration of {DURATION} starting from the given date.
    4. Distribute the time into distinct hours that make sense for studying.
    5. Do not exceed a maximum of {DAILY_LIMIT} hours per day.
    5. Avoid choosing hours that are close to the existing schedule.
    6. Prioritize hours that are in empty time blocks.
    7. Do NOT write any explanatory text.
    8. Return ONLY using the set_freetime function with the generated data.

    """

    # Configure the tools
    tools = types.Tool(function_declarations=[set_freetime_function])
    config = types.GenerateContentConfig(
        tools=[tools],
        system_instruction= [
            prompt_days,
            prompt_schedulers,
            prompt_base
        ]
    )
    return request_AI_response(config, date)

# 2.
# Creation of study modules
def modules_definition(theme, total_free_time):
    MODULE_SCHEMA = {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "Name of the study module."
            },
            "description": {
                "type": "string",
                "description": "A short description about the importance of studying this topic."
            }
        },
        "required": ["name", "description"]
    }

    # Define the function declaration for the model
    study_modules_function = {
        "name": "study_modules",
        "description": "Creates study modules based on the topic.",
        "parameters": {
            "type": "object",
            "properties": {
                "modules": {
                    "type": "array",
                    "items": MODULE_SCHEMA
                }
            },
            "required": ["modules"]
        }
    }

    # PROMPT — 
    prompt_base = f"""
    The user will indicate what they want to study.".

    Your task is:
    1. Create an organized study plan with modules and activities.
    2. Reasonable duration of {DURATION} based on the topic, with a maximum total duration of up to {total_free_time} hours.
    3. The title (name) should avoid unnecessary punctuation, avoid long sentences, and not repeat words already clear in the module.
    4. Do NOT write explanatory text.
    5. Return ONLY using the study_modules function with the generated data.

    """

    # Configure the tools
    tools = types.Tool(function_declarations=[study_modules_function])
    config = types.GenerateContentConfig(
        tools=[tools],
        system_instruction= [
            prompt_base
        ]
    )
    return request_AI_response(config, theme)

# 3.
# Task priority definition
def priorities_definition(modules_schema):
    # Define the function declaration for the model
    set_priorities_function =  {
        "name": "set_priorities",
        "description": "Relate the appropriate priority for each study module.",
        "parameters": {
            "type": "object",
            "properties": {
                "priorities": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Name of the study module."
                            },
                            "priority_id": {
                                "type": "integer",
                                "description": "Priority ID related to the priority list."
                            }
                        }
                    }
                }
            },
            "required": ["priorities"]
        }
    }

    # Load Priorities from database 
    priorities = init_db.load_priorities()
    prompt_priorities = f"""
    When setting priority_id, use these priorities as reference.".

    Priorities list:
    {priorities}

    """

    # PROMPT — 
    prompt_base = f"""
    The user will provide the modules they want to study".

    Your task is:
    1. Relate each module to a priority from the priority list.
    2. The priority must be distributed among the module items according to the relevance of the subject.
    3. Do NOT write explanatory text.
    4. Return ONLY using the set_priorities function with the generated data.

    """

    # Configure the tools
    tools = types.Tool(function_declarations=[set_priorities_function])
    config = types.GenerateContentConfig(
        tools=[tools],
        system_instruction= [
            prompt_priorities,
            prompt_base
        ]
    )
    return request_AI_response(config, modules_schema)

# 4.
# Resolve priorities relationship with module
def priorities_relationships(priorities_schema, modules_schema):

    priorities_map = {}

    for priority in priorities_schema['priorities']:
            priorities_map[priority['name']] = priority['priority_id']

    for module in modules_schema['modules']:
        module['priority_id'] = priorities_map[module['name']]
    
    return modules_schema

# Applying scientific study methods
def methods_apply(hours_schema, modules_schema):
    # Define the function declaration for the model
    study_schedule_function = {
        "name": "study_schedule",
        "description": "Schedule based on provided lists of hours and modules.",
        "parameters": {
            "type": "object",
            "properties": {
                "schedules": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "duration": {"type": "integer", "description": "Module duration in minutes from 1 to 60."},
                            "date": {"type": "string"},
                            "hour": {"type": "integer"},
                            "annotation": {"type": "string"},
                            "priority_id": {"type": "integer"}
                        },
                        "required": ["name", "duration", "date", "hour", "annotation", "priority_id"]
                    }
                }
            },
            "required": ["schedules"]
        }
    }
    
    # PROMPT — 
    prompt_base = f"""
    The user will provide the modules they want to study and the hours they have available".

    Your task is:
    1. Create an organized study plan based on available free time.
    2. Structure the modules using proven learning techniques, distributing the content as efficiently as possible.
    3. Prioritize a balanced distribution of cognitive load, avoiding excessively long blocks.
    4. The duration settings must vary between 1 and 60 minutes.
    5. Do NOT write explanatory text.
    6. Return ONLY using the study_schedule function with the generated data.
    
    """

    # PROMPT — 
    prompt_lists = f"""
    Hours list:
    {hours_schema}

    Modules list:
    {modules_schema}

    """

    # Configure the tools
    tools = types.Tool(function_declarations=[study_schedule_function])
    config = types.GenerateContentConfig(
        tools=[tools],
        system_instruction= [
            prompt_base
        ],
    )
    response = request_AI_response(config, prompt_lists)

    return init_db.save_data(response)