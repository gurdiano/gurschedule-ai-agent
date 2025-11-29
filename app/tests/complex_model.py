import os
from google import genai
from google.genai import types
from model import init_db
from dotenv import load_dotenv

load_dotenv()
GEMINI_KEY = os.getenv('GEMINI_API_KEY')
OPEN_TIME = os.getenv('OPEN_TIME')
CLOSE_TIME = os.getenv('CLOSE_TIME')

# Define the personal Schemas
day_obj = {
    "type": "object",
    "properties": {
        "id": { 
            "type": "integer",
            "description": "Caso já possua data existente na lista pegar o id equivalente, caso não passar None"
        },
        "date": { 
            "type": "string",
            "description": "Data para o estudo (e.g., 'yyyy-mm-dd')"
        }
    },
    "required": ["date"]
}
task_obj = {
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "description": "Nome do modulo estudado"
        },
        "duration": {
            "type": "integer",
            "description": "Duração do estudo de 0 à 60 minutos"
        },
        "icon_id": {
            "type": "integer",
            "description": "Sempre o número 66"
        }
    },
    "required": ["name", "duration", "icon_id"]
}
scheduler_obj = {
    "type": "object",
    "properties": {
        "hour": {
            "type": "integer",
            "description": "Hora em que se deseja iniciar o estudo"
        },
        "annotation": {
            "type": "string",
            "description": "Breve descrição sobre o motivo por qual realizar esse estudo"
        },
        "day": day_obj,
        "task": task_obj,
        "priority_id": {
            "type": "integer",
            "description": "Escolher um id da lista de prioridades conforme mais adequado para o estudo"
        }
    },
    "required": ["hour", "annotation", "day", "task", "priority_id"]
}

# Define the personal function declaration for the model
teste_study_plan_function = {
    "name": "teste_study_plan",
    "description": "Cria um plano de estudo baseado no tema informado pelo usuário.",
    "parameters": {
        "type": "object",
        "properties": {
            "tema": {"type": "string"},
            "modulos": {
                "type": "array",
                "items": scheduler_obj
            }
        },
        "required": ["tema", "modulos"]
    },
}

# Current Date
import datetime 
today = datetime.date.today()

# PROMPT — 
prompt_base = f"""
O usuário vai informar que deseja estudar".

Sua tarefa é:
1. Criar um plano de estudo organizado com módulos e atividades.
2. Duração razoável de 1 semana baseada no tema, à partir da data {today}.
3. NÃO escreva texto explicativo.
4. Retorne SOMENTE usando a função teste_study_plan com os dados gerados.
5. Não criar nenhum estudo que conflite com taréfas já existentes na lista de agendamentos.
6. Usar janela de TODOS os horários disponível das {OPEN_TIME} às {CLOSE_TIME}.
7. A prioridade deve ser distribuidade entre os itens no modulo conforme o grau do assunto.
8. Se necessário os mesmos modulos de estudos podem se repitir mais de uma vez ao dia.
9. Aplicar técnicas comprovadas de aprendizagem: 
   - alternância de assuntos relacionados (interleaving),
   - revisões espaçadas (spaced repetition),
   - exercícios de recordação ativa (active recall).
10. Incluir sessões curtas de revisão diária dos módulos já estudados.
11. Garantir que cada módulo possua objetivos claros, mensuráveis e de baixa ambiguidade.
12. Dividir tópicos complexos em partes menores (chunking) mantendo progressão lógica.
13. Priorizar distribuição equilibrada de carga cognitiva evitando blocos excessivamente longos.
14. Incluir breves pausas entre sessões de estudo quando ultrapassarem 60 minutos.
15. Ajustar automaticamente a duração total dos módulos para caber no período variável definido pelo usuário.
16. Se o tempo total de estudo disponível for curto, priorizar os tópicos de maior impacto para o aprendizado.
17. Garantir que cada dia tenha pelo menos:
    - 1 sessão de estudo principal,
    - 1 sessão de revisão curta,
    - 1 exercício prático (se aplicável ao tema).
18. Evitar colocar módulos novos imediatamente após módulos muito densos; alternar com revisão ou prática.
19. Se for detectado que o usuário já estudou um módulo anteriormente, intensificar revisões espaçadas ao invés de repetição total.
20. Quando necessário repetir módulos no mesmo dia, variar o tipo da atividade (ex.: leitura → prática → revisão).
21. O título (name) deve evitar pontuação desnecessária, não usar frases longas e não repetir palavras já claras no módulo.
22. A anotação deve esclarecer por que essa tarefa é importante para o progresso no módulo, relacionando-a ao objetivo geral do estudo.

"""


# Load Priorities from database 
priorities = init_db.load_priorities()

prompt_priorities = f"""
Quando for definir priority_id usar como base essas prioridades".

Lista de prioridades:
{priorities}

"""

# Load Days from database
days = init_db.load_days()

prompt_days = f"""
Lista de dias já existentes para base".

Lista de dias:
{days}

"""

# Load Schedulers from database
schedulers = init_db.load_schedulers()

prompt_schedulers = f"""
Lista das tarefas agendadas já existentes para base".

Lista de agendamentos:
{schedulers}

"""

# Configure the client and tools
client = genai.Client(api_key=GEMINI_KEY)
tools = types.Tool(function_declarations=[teste_study_plan_function])
config = types.GenerateContentConfig(
    tools=[tools],
    system_instruction= [
        prompt_days,
        prompt_priorities,
        prompt_schedulers,
        prompt_base
    ]
)

# teste
def ask_to_ia(tema_usuario):
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=tema_usuario,
            config=config,
        )

        # Detecta chamada de função
        if response.candidates[0].content.parts[0].function_call:
            function_call = response.candidates[0].content.parts[0].function_call
            print(f"Function to call: {function_call.name}")
            print(f"Arguments: {function_call.args}")

            # init_db.save_data(function_call.args)

            return function_call.args
        else:
            print("O modelo retornou texto ao invés de function_call:", response.text)
            return response.text
    except Exception as e:
        raise e
        # print(f'olha a response = {response}')