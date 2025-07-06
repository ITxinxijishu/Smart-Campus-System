import os
from django.conf import settings
import random
import string

def get_data_path(filename):
    return os.path.join(settings.BASE_DIR, 'data', filename)

def read_lines(filename):
    """读取文件内容，返回行列表"""
    path = get_data_path(filename)
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return []

def write_lines(filename, lines):
    """将行列表写入文件"""
    path = get_data_path(filename)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

def append_line(filename, line):
    """在文件末尾追加一行"""
    path = get_data_path(filename)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'a', encoding='utf-8') as f:
        f.write(line + '\n')

def find_line(filename, condition):
    """查找满足条件的行"""
    lines = read_lines(filename)
    for line in lines:
        parts = line.split(',')
        if condition(parts):
            return parts
    return None

def find_lines(filename, condition):
    """查找所有满足条件的行"""
    lines = read_lines(filename)
    return [line.split(',') for line in lines if condition(line.split(','))]

def update_line(filename, condition, new_data):
    """更新满足条件的行"""
    lines = read_lines(filename)
    updated = False
    for i, line in enumerate(lines):
        parts = line.split(',')
        if condition(parts):
            lines[i] = ','.join(new_data)
            updated = True
            break
    if updated:
        write_lines(filename, lines)
    return updated

def generate_random_code(length=6):
    """生成随机识别码"""
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

# 用户认证相关
def authenticate(username, password):
    """用户认证"""
    user = find_line('auth/users.txt', 
                    lambda parts: parts[0] == username and parts[1] == password)
    return user

def register_user(username, password, role, real_name, shibiema):
    """注册用户"""
    # 验证识别码
    shibiema_data = find_line('auth/shibiema.txt', 
                             lambda parts: parts[4] == shibiema)
    if not shibiema_data:
        return False, "无效的识别码"
    
    # 检查用户名是否已存在
    if find_line('auth/users.txt', lambda parts: parts[0] == username):
        return False, "用户名已存在"
    
    # 添加新用户
    school_id = shibiema_data[0]
    class_id = shibiema_data[2]
    new_user = f"{username},{password},{role},{real_name},{school_id},{class_id}"
    append_line('auth/users.txt', new_user)
    return True, "注册成功"

# 学校管理
def get_schools():
    """获取所有学校"""
    shibiema_lines = read_lines('auth/shibiema.txt')
    schools = {}
    for line in shibiema_lines:
        parts = line.split(',')
        school_id = parts[0]
        school_name = parts[1]
        if school_id not in schools:
            schools[school_id] = {
                'id': school_id,
                'name': school_name,
                'classes': []
            }
        schools[school_id]['classes'].append({
            'class_id': parts[2],
            'class_name': parts[3],
            'shibiema': parts[4]
        })
    return schools

def add_school(school_name):
    """添加新学校"""
    schools = get_schools()
    # 生成新学校ID
    new_id = str(max([int(k) for k in schools.keys()] + [0]) + 1)
    # 添加默认班级
    class_id = "1"
    class_name = school_name + "默认班级"
    shibiema = generate_random_code()
    new_line = f"{new_id},{school_name},{class_id},{class_name},{shibiema}"
    append_line('auth/shibiema.txt', new_line)
    return new_id

def add_class(school_id, class_name):
    """为学校添加新班级"""
    shibiema_lines = read_lines('auth/shibiema.txt')
    # 找到该学校的最大班级ID
    max_class_id = 0
    for line in shibiema_lines:
        parts = line.split(',')
        if parts[0] == school_id:
            class_id = int(parts[2])
            if class_id > max_class_id:
                max_class_id = class_id
    new_class_id = str(max_class_id + 1)
    shibiema = generate_random_code()
    school_name = find_line('auth/shibiema.txt', 
                           lambda parts: parts[0] == school_id)[1]
    new_line = f"{school_id},{school_name},{new_class_id},{class_name},{shibiema}"
    append_line('auth/shibiema.txt', new_line)
    return new_class_id

# 作业管理
def create_homework(school_id, class_id, subject, title, content, due_date, creator):
    """创建新作业"""
    filename = f"homework/assignments/{school_id}_{class_id}.txt"
    lines = read_lines(filename)
    # 生成新作业ID
    new_id = str(len(lines) + 1)
    new_homework = f"{new_id},{subject},{title},{content},{due_date},{creator}"
    append_line(filename, new_homework)
    return new_id

def get_homeworks(school_id, class_id):
    """获取班级所有作业"""
    filename = f"homework/assignments/{school_id}_{class_id}.txt"
    homeworks = []
    for line in read_lines(filename):
        parts = line.split(',')
        homeworks.append({
            'id': parts[0],
            'subject': parts[1],
            'title': parts[2],
            'content': parts[3],
            'due_date': parts[4],
            'creator': parts[5]
        })
    return homeworks

def submit_homework(homework_id, school_id, class_id, username, content):
    """提交作业"""
    # 获取作业信息
    homeworks = get_homeworks(school_id, class_id)
    homework = next((h for h in homeworks if h['id'] == homework_id), None)
    if not homework:
        return False, "作业不存在"
    
    # 获取学生信息
    student = find_line('auth/users.txt', lambda parts: parts[0] == username)
    if not student or student[2] != 'student':
        return False, "学生信息错误"
    
    # 保存提交
    filename = f"homework/submissions/{school_id}_{class_id}_{homework_id}_{username}.txt"
    submission = f"{homework_id},{student[3]},{content},{timezone.now().strftime('%Y-%m-%d %H:%M')},已提交"
    write_lines(filename, [submission])
    return True, "提交成功"

def get_student_homeworks(school_id, class_id, username):
    """获取学生作业及提交状态"""
    homeworks = get_homeworks(school_id, class_id)
    result = []
    for hw in homeworks:
        # 检查是否已提交
        filename = f"homework/submissions/{school_id}_{class_id}_{hw['id']}_{username}.txt"
        submitted = os.path.exists(get_data_path(filename))
        
        result.append({
            'id': hw['id'],
            'subject': hw['subject'],
            'title': hw['title'],
            'due_date': hw['due_date'],
            'status': '已提交' if submitted else '未提交'
        })
    return result

# 课程表管理
def get_timetable(school_id, class_id):
    """获取课程表"""
    filename = f"timetable/{school_id}_{class_id}.txt"
    timetable = []
    for line in read_lines(filename):
        parts = line.split(',')
        timetable.append({
            'day': parts[0],
            'period': parts[1],
            'subject': parts[2],
            'teacher': parts[3]
        })
    return timetable

def save_timetable(school_id, class_id, timetable):
    """保存课程表"""
    filename = f"timetable/{school_id}_{class_id}.txt"
    lines = []
    for item in timetable:
        lines.append(f"{item['day']},{item['period']},{item['subject']},{item['teacher']}")
    write_lines(filename, lines)