import app.global_vars as global_vars
import re


def appointments_key(hour):
    # Map hours to their positions in the desired order (7am to 6am)
    if 7 <= hour <= 23:
        return hour - 7
    elif 0 <= hour < 7:
        return hour + 17
    else:
        raise ValueError("Hour should be in the range 0-23")


def appointments_letters_key(s):
    letters = ['dn', 'd', 'm', 't', 'n', 'c', 'v', 'x']

    for letter in letters:
        if letter in s:
            return letters.index(letter)
    
    raise ValueError("String should contain one of the following letters: dn, d, m, t, n, c, v, x")


def prepare_appointments(appointments):
    """convert a list of appointments to a list of hours and a remainder"""
        
    hours_map = global_vars.HOURS_MAP
    appointments = sorted(appointments, key=appointments_key)

    letters = []
    for letter, hour in hours_map.items():
        hour_list = gen_hour_range(hour)

        if set(hour_list).issubset(set(appointments)):
            letters.append(letter)
            appointments = [app for app in appointments if app not in hour_list]
   
    letters = sorted(letters, key=appointments_letters_key)

    return letters, appointments


def split_hours(hour_list):
    """splits a list of hours into consecutive ranges of hours, representing periods of the day"""
    hours_key = global_vars.HOURS_KEY
    if not hour_list:
        return []
    
    hour_list = sorted(hour_list, key=lambda x: hours_key.index(x))

    split_hours = []
    current = [hour_list[0]]
    for i in range(1, len(hour_list)):
        if hour_list[i] == hour_list[i - 1] + 1 or hour_list[i] == 0 and hour_list[i - 1] == 23:
            current.append(hour_list[i])
        else:
            split_hours.append(current)
            current = [hour_list[i]]
    
    split_hours.append(current)
    split_hours = sorted(split_hours, key=lambda x: x[0])

    return split_hours


def gen_hour_range(hours):
    """enter a tuple and get a list of a range"""
    starting_hour, ending_hour = hours

    if starting_hour == ending_hour == 7:
        return list(range(7, 24)) + list(range(0, 7))
    if starting_hour == ending_hour:
        return []
    if starting_hour < ending_hour:
        return list(range(hours[0], hours[1]+1))
    if starting_hour > ending_hour:
        return [h for h in range(hours[0], 24)] + [h for h in range(hours[1]+1)]


def gen_redudant_hour_list(appointments, include_line=False):
    """Generates a list of hours that includes both the longer periods (d, n)
       and their subperiods (m, t, c, v). If include_line is True, the list will
       include a string representing the period of time"""
    if appointments == []:
        return []
    
    hours_map = global_vars.HOURS_MAP
    letters, remainder = prepare_appointments(appointments)

    for letter in letters:
        if len(letter) > 1:
            letters.extend(list(letter))
    if 'd' in letters:
        letters += ['m', 't']
    if 'n' in letters:
        letters += ['c', 'v']

    letters = sorted(letters, key=appointments_letters_key)
    lines = [f"{l}: {hours_map[l][0]:02d}:00 - {hours_map[l][1]+1:02d}:00" for l in letters]

    if not remainder:
        if not include_line:
            return letters
        return lines
    
    if max(remainder) - min(remainder) != len(remainder) - 1:
        if not include_line:
            return letters + [f'x{len(remainder)}']
        return lines + [f"x{len(remainder)}: {remainder[0]:02d}:00 - {remainder[-1]+1:02d}:00"]
    
    for letter, hour in list(hours_map.items())[2:]:
        hour_list = gen_hour_range(hour)

        if set(appointments).issubset(set(hour_list)):
            lt = f"{letter}{len([app for app in appointments if app in hour_list])}"
            letters.append(lt)
            lines.append(f"{lt}: {appointments[0]:02d}:00 - {appointments[-1]+1:02d}:00")

        elif remainder and set(remainder).issubset(set(hour_list)):
            lt = f"{letter}{len([app for app in remainder if app in hour_list])}"
            letters.append(lt)
            lines.append(f"{lt}: {remainder[0]:02d}:00 - {remainder[-1]+1:02d}:00")

    letters = sorted(letters, key=appointments_letters_key)

    if not include_line:
        return letters

    return sorted(lines, key=appointments_letters_key)
        

def convert_to_letter(appointments):
    """converts a list of appointments to a string of letters
       incomplete periods are represented as the letter for the period and an int for the number of hours
       non-consecutive hours are marked as an x followed by the number of hours"""
    if appointments == []:
        return []
    
    hours_map = global_vars.HOURS_MAP
    letters, remainder = prepare_appointments(appointments)

    if not remainder:
        return ''.join(letters)
    
    if max(remainder) - min(remainder) != len(remainder) - 1:
        letters.append(f'x{len(remainder)}')
        return ''.join(letters)

    for letter, hour in list(hours_map.items())[::-1]:
        hour_list = gen_hour_range(hour)

        if remainder and set(remainder).issubset(set(hour_list)):
            letters.append(f"{letter}{len([app for app in remainder if app in hour_list])}")
            remainder = [app for app in remainder if app not in hour_list]

    return ''.join(letters)


def convert_letter_to_hours(letter):
    """convert a string of letters to a list of hours"""
    hours_map = global_vars.HOURS_MAP
    
    if not letter:
        return []
    
    pattern = re.compile(r'[A-Za-z](?:\d+)?')
    
    string_list = pattern.findall(letter)
    string_list = sorted(string_list, key=appointments_letters_key)

    appointments = []
    for item in string_list:
        if item in hours_map:
            appointments += gen_hour_range(hours_map.get(item))
        else:
            letter = item[0]
            number = int(item[1:])

            if letter == 'x':
                return 1

            hours_tuple = hours_map.get(letter)

            appointments += gen_hour_range((hours_tuple[0], hours_tuple[0] + number-1))

    return appointments


def convert_hours_to_line(hour_list):
    if not hour_list:
        return ""
    starting_hour = hour_list[0]
    ending_hour = hour_list[-1]+1 if hour_list[-1] != 23 else 0
    return f"{starting_hour:02d}:00 - {ending_hour:02d}:00"


def convert_line_to_hour(line):
    """convert a string representing a period of time to a list of hours"""
    if not line:
        return []
   
    start_hour, end_hour = [int(h.split(":")[0]) for h in line.split(": ")[1].split(" - ")]
    hour_range = gen_hour_range((start_hour, end_hour-1))

    return hour_range


def convert_hours(hour_list):
    """convert the string hour list from the frontend to a list of integers
    Hour_list has the format ["-", "00:00", "00:00"]"""
    hours_map = global_vars.HOURS_MAP

    if hour_list[0] == "-":
        start_hour, end_hour = int(hour_list[1].split(":")[0]), int(hour_list[2].split(":")[0])
        if start_hour == end_hour and not start_hour == 7:
            return "Horários Inválidos - A hora de Início e de Fim são iguais"
        
        if start_hour >= end_hour:
            hours = list(range(start_hour, 24)) + list(range(end_hour))
        else:
            hours = list(range(start_hour, end_hour))
    else:
        start_hour, end_hour = hours_map[hour_list[0]]
        
        if start_hour > end_hour:
            hours = list(range(start_hour, 24)) + list(range(end_hour + 1))
        else:
            hours = list(range(start_hour, end_hour + 1))

    if 7 in hours[1:]:
        return "Horários Inválidos - A hora de Fim Passa para o Dia Seguinte"

    return hours
