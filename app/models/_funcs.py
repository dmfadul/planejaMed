import instance.global_vars as global_vars


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

    unified_appointments = sorted(unified_appointments, key=lambda x: ['d', 'm', 't', 'n', 'c', 'v'].index(x))

    if not unified_appointments:
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
