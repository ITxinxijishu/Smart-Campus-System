import os
from django.conf import settings
import datetime

def get_banji_path():
    return os.path.join(settings.BASE_DIR, 'banji.txt')

def get_class_path(class_id):
    return os.path.join(settings.BASE_DIR, f'{class_id}.txt')

def get_shibiema_path():
    return os.path.join(settings.BASE_DIR, 'shibiema.txt')

def get_schools_path():
    return os.path.join(settings.BASE_DIR, 'schools.txt')

def get_timetable_path(class_name):
    return os.path.join(settings.BASE_DIR, f'timetable_{class_name}.txt')

def read_all_banji():
    try:
        with open(get_banji_path(), 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return []

def save_all_banji(banji_list):
    with open(get_banji_path(), 'w', encoding='utf-8') as f:
        f.write('\n'.join(banji_list))

def read_class_students(class_id):
    try:
        with open(get_class_path(class_id), 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return []

def save_class_students(class_id, students):
    with open(get_class_path(class_id), 'w', encoding='utf-8') as f:
        f.write('\n'.join(students))

def class_exists(class_id):
    return os.path.exists(get_class_path(class_id))

def save_shibiema(shibiema_list):
    with open(get_shibiema_path(), 'w', encoding='utf-8') as f:
        f.write('\n'.join(shibiema_list))

def read_all_shibiema():
    try:
        with open(get_shibiema_path(), 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return []

def save_school(schools_list):
    with open(get_schools_path(), 'w', encoding='utf-8') as f:
        f.write('\n'.join(schools_list))

def read_all_schools():
    try:
        with open(get_schools_path(), 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return []

def save_timetable(class_name, timetable):
    with open(get_timetable_path(class_name), 'w', encoding='utf-8') as f:
        f.write('\n'.join(timetable))

def read_timetable(class_name):
    try:
        with open(get_timetable_path(class_name), 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return []

def get_current_reset_time():
    """获取当前重置时间"""
    time_path = os.path.join(settings.BASE_DIR, 'time.txt')
    try:
        with open(time_path, 'r', encoding='utf-8') as f:
            times = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return None

    reset_times = []
    for t in times:
        try:
            hour, minute = map(int, t.split(':'))
            reset_times.append(datetime.time(hour, minute))
        except ValueError:
            continue

    if not reset_times:
        return None

    reset_times.sort()
    now = datetime.datetime.now().time()
    current_reset_time = None

    for rt in reset_times:
        if rt <= now:
            current_reset_time = rt
        else:
            break

    if current_reset_time is None:
        current_reset_time = reset_times[-1]

    return current_reset_time