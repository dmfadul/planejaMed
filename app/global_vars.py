from datetime import datetime


STR_DAY = 26
END_DAY = STR_DAY - 1

LEADER = "DR. VICTOR HUGO MARCASSA"

MORNING_START, MORNING_END = 7, 12
AFTERNOON_START, AFTERNOON_END = 13, 18
CINDERELLA_START, CINDERELLA_END = 19, 0
VAMPIRE_START, VAMPIRE_END = 1, 6

HOURS_MAP = {
             'dn': (MORNING_START, VAMPIRE_END),
             'dc': (MORNING_START, CINDERELLA_END),
             'd': (MORNING_START, AFTERNOON_END),
             'n': (CINDERELLA_START, VAMPIRE_END),
             'm': (MORNING_START, MORNING_END),
             't': (AFTERNOON_START, AFTERNOON_END),
             'c': (CINDERELLA_START, CINDERELLA_END),
             'v': (VAMPIRE_START, VAMPIRE_END),
            #  'tn': (AFTERNOON_START, VAMPIRE_END),
             }

MAJOR_HOURS = ['d', 'n', 'dc', 'dn']

HOURS_KEY = list(range(MORNING_START, 24)) + list(range(VAMPIRE_END + 1))

NIGHT_HOURS = list(range(CINDERELLA_START, 24)) + list(range(VAMPIRE_END + 1))

DIAS_SEMANA = ["SEGUNDA", "TERÇA", "QUARTA", "QUINTA", "SEXTA", "SABADO", "DOMINGO"]

MESES = [
        "JANEIRO",
        "FEVEREIRO",
        "MARÇO",
        "ABRIL",
        "MAIO",
        "JUNHO",
        "JULHO",
        "AGOSTO",
        "SETEMBRO",
        "OUTUBRO",
        "NOVEMBRO",
        "DEZEMBRO"
        ]


SYSTEM_CRM = 0

VACATION_NEW_RULES = {"routine": 104, "plaintemps": 36}
VACATION_OLD_RULES = {"routine": 52, "plaintemps": 36}
VACATION_NEW_RULE_START = datetime(year=2023, month=12, day=8)

MAX_VACATION_SPLIT = 2
MIN_VACATION_DURATION = 7
TOTAL_VACATION_DAYS = 15
SICK_LEAVE_TO_VACATION = 3

MINIMUM_MONTHS_COMPLIENCE_FOR_VACATION = 6

TRANSLATION_DICT = {
    "pending_approval": "Pendente",
    "defered": "Deferido",
    "approved": "Aprovado",
    "denied": "Negado",
    "completed": "Concluído",
    "ongoing": "Em andamento",
    "paid": "Pago",
    "unapproved": "Aprovação Retirada",
    "archived": "Arquivado",
    "deleted": "Apagado",
}