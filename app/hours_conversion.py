import app.global_vars as global_vars


def unify_appointments(appointments):
    if appointments == []:
        return []
    
    hours_map = global_vars.HOURS_MAP
    appointments = sorted(appointments)

    unified_appointments = []
    for letter, hour in hours_map.items():
        if hour[0] < hour[1]:
            hour_list = list(range(hour[0], hour[1]+1))
        else:
            hour_list = [h for h in range(hour[0], 25)] + [h for h in range(1, hour[1]+1)]

        if set(hour_list).issubset(set(appointments)):
            unified_appointments.append(letter)
            appointments = [app for app in appointments if app not in hour_list]

    unified_appointments = sorted(unified_appointments, key=lambda x: ['dn', 'd', 'm', 't', 'n', 'c', 'v'].index(x))

    if not appointments:
        return ''.join(unified_appointments)

    for letter, hour in list(hours_map.items())[::-1]:
        if hour[0] < hour[1]:
            hour_list = list(range(hour[0], hour[1]+1))
        else:
            hour_list = [h for h in range(hour[0], 25)] + [h for h in range(1, hour[1]+1)]
        if appointments and set(appointments).issubset(set(hour_list)):
            unified_appointments.append(f"{letter}{len([app for app in appointments if app in hour_list])}")
            appointments = [app for app in appointments if app not in hour_list]

    return ''.join(unified_appointments)


def split_hours(hour_list):
    hours_key = global_vars.HOURS_KEY
    if not hour_list:
        return []
    
    hour_list = sorted(hour_list, key=lambda x: hours_key.index(x))

    split_hours = []
    current = [hour_list[0]]
    for i in range(1, len(hour_list)):
        if hour_list[i] == hour_list[i - 1] + 1 or hour_list[i] == 1 and hour_list[i - 1] == 24:
            current.append(hour_list[i])
        else:
            split_hours.append(current)
            current = [hour_list[i]]
    
    split_hours.append(current)
    split_hours = sorted(split_hours, key=lambda x: x[0])

    return split_hours


def convert_hours_to_line(hour_list):
    if not hour_list:
        return ""
    
    if len(hour_list) == 1:
        return -1
    
    return f"{hour_list[0]:02d}:00 - {hour_list[-1]:02d}:00"
