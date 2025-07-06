import os
import random
import datetime
from django.shortcuts import render, redirect
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from django.db.models import Count, Max
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Attendance, User, School, Shibiema, Homework, HomeworkSubmission, Timetable
from .file_utils import (get_banji_path, get_class_path, class_exists, 
                         read_all_banji, save_all_banji, read_class_students, 
                         save_class_students, get_shibiema_path, save_shibiema, 
                         read_all_shibiema, get_schools_path, save_school, 
                         read_all_schools, get_timetable_path, save_timetable, 
                         read_timetable, get_current_reset_time)

def index(request):
    """首页视图 - 随机点名系统"""
    banji_path = get_banji_path()
    try:
        with open(banji_path, 'r', encoding='utf-8') as f:
            classes = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        classes = []

    selected_student = None
    selected_class = None
    current_reset_time = get_current_reset_time()

    last_selected_class = request.session.get('last_selected_class')
    last_selected_student = request.session.get('last_selected_student')

    if request.method == 'POST':
        selected_class = request.POST.get('class_num')
        if selected_class:
            request.session['last_selected_class'] = selected_class
            last_reset = cache.get(f'{selected_class}_last_reset')
            need_initialize = last_reset != current_reset_time

            try:
                if need_initialize:
                    file_path = get_class_path(selected_class)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        students = [line.strip() for line in f if line.strip()]
                    random.shuffle(students)
                    cache.set(f'{selected_class}_remaining', students.copy(), None)
                    cache.set(f'{selected_class}_called', [], None)
                    cache.set(f'{selected_class}_last_reset', current_reset_time, None)
                else:
                    remaining = cache.get(f'{selected_class}_remaining')
                    if not remaining:
                        file_path = get_class_path(selected_class)
                        with open(file_path, 'r', encoding='utf-8') as f:
                            students = [line.strip() for line in f if line.strip()]
                        random.shuffle(students)
                        cache.set(f'{selected_class}_remaining', students.copy(), None)
                        cache.set(f'{selected_class}_called', [], None)

                remaining = cache.get(f'{selected_class}_remaining')
                called = cache.get(f'{selected_class}_called')

                if remaining:
                    selected_student = remaining.pop(0)
                    called.append(selected_student)
                    cache.set(f'{selected_class}_remaining', remaining, None)
                    cache.set(f'{selected_class}_called', called, None)
                    
                    Attendance.objects.create(
                        student_name=selected_student,
                        class_name=selected_class,
                        timestamp=timezone.now()
                    )
                else:
                    selected_student = "所有学生都已点名"
                    Attendance.objects.create(
                        student_name="点名完成",
                        class_name=selected_class,
                        timestamp=timezone.now()
                    )

                request.session['last_selected_student'] = selected_student

            except FileNotFoundError:
                selected_student = "班级文件不存在"
                Attendance.objects.create(
                    student_name="错误：班级文件不存在",
                    class_name=selected_class,
                    timestamp=timezone.now()
                )

    else:
        selected_class = last_selected_class
        selected_student = last_selected_student

    recent_attendance = Attendance.objects.values('timestamp__date')\
        .annotate(date_count=Count('id'))\
        .order_by('-timestamp__date')[:7]
    
    class_totals = Attendance.objects.values('class_name')\
        .annotate(total=Count('id'))\
        .order_by('-total')
    
    return render(request, 'index.html', {
        'classes': classes,
        'selected_student': selected_student,
        'selected_class': selected_class,
        'current_reset_time': current_reset_time,
        'recent_attendance': recent_attendance,
        'class_totals': class_totals
    })

def attendance_statistics(request):
    """点名统计视图"""
    banji_path = get_banji_path()
    
    classes = []
    if os.path.exists(banji_path):
        with open(banji_path, 'r', encoding='utf-8') as f:
            classes = [line.strip() for line in f if line.strip()]
    
    class_stats = Attendance.objects.values('class_name').annotate(
        total_attendances=Count('id'),
        last_time=Max('timestamp')
    ).order_by('-total_attendances')
    
    date_stats = Attendance.objects.values('timestamp__date').annotate(
        total_attendances=Count('id'),
        last_time=Max('timestamp')
    ).order_by('-timestamp__date')
    
    student_stats = Attendance.objects.values('student_name').annotate(
        total_attendances=Count('id'),
        last_time=Max('timestamp')
    ).order_by('-total_attendances')
    
    class_student_stats = Attendance.objects.values(
        'class_name', 'student_name'
    ).annotate(
        total_attendances=Count('id'),
        last_time=Max('timestamp')
    ).order_by('-total_attendances')
    
    date_student_stats = Attendance.objects.values(
        'timestamp__date', 'student_name'
    ).annotate(
        total_attendances=Count('id'),
        last_time=Max('timestamp')
    ).order_by('-total_attendances')
    
    class_date_stats = Attendance.objects.values(
        'class_name', 'timestamp__date'
    ).annotate(
        total_attendances=Count('id'),
        last_time=Max('timestamp')
    ).order_by('-total_attendances')
    
    return render(request, "attendance/statistics.html", {
        'classes': classes,
        'class_stats': class_stats,
        'date_stats': date_stats,
        'student_stats': student_stats,
        'class_student_stats': class_student_stats,
        'date_student_stats': date_student_stats,
        'class_date_stats': class_date_stats
    })

def role_select(request):
    """角色选择视图"""
    if request.method == 'POST':
        request.session['register_role'] = request.POST.get('role')
        return redirect('register')
    return render(request, 'auth/role_select.html')

def register(request):
    """用户注册视图"""
    role = request.session.get('register_role', 'student')
    role_display = {
        'student': '学生',
        'teacher': '教师',
        'education': '教育管理员'
    }.get(role, '用户')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        real_name = request.POST.get('real_name')
        shibiema = request.POST.get('shibiema')
        
        if password != password2:
            messages.error(request, '两次输入的密码不一致')
            return redirect('register')
        
        # 验证识别码
        shibiema_data = read_all_shibiema()
        valid_shibiema = False
        school_name = None
        class_name = None
        
        for line in shibiema_data:
            if shibiema == line.split(',')[0]:
                valid_shibiema = True
                school_name = line.split(',')[1]
                class_name = line.split(',')[2]
                break
        
        if not valid_shibiema:
            messages.error(request, '无效的识别码')
            return redirect('register')
        
        # 创建用户
        try:
            user = User.objects.create_user(
                username=username,
                password=password,
                role=role,
                real_name=real_name,
                school_code=shibiema,
                class_name=class_name
            )
            login(request, user)
            messages.success(request, '注册成功！')
            return redirect('dashboard')
        except Exception as e:
            messages.error(request, f'注册失败: {str(e)}')
    
    return render(request, 'auth/register.html', {
        'role': role,
        'role_display': role_display
    })

def user_login(request):
    """用户登录视图"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, '用户名或密码错误')
    
    return render(request, 'auth/login.html')

@login_required
def user_logout(request):
    """用户登出视图"""
    logout(request)
    return redirect('index')

@login_required
def dashboard(request):
    """控制台视图 - 根据角色重定向"""
    user = request.user
    if user.role == 'education':
        return redirect('shibiema_manage')
    elif user.role == 'teacher':
        return redirect('teacher_homework_list')
    elif user.role == 'student':
        return redirect('student_dashboard')
    return redirect('index')

def manage_banji(request):
    """班级管理视图"""
    if request.method == 'POST':
        if 'add_banji' in request.POST:
            new_id = request.POST.get('new_id')
            if new_id:
                banji_list = read_all_banji()
                if new_id not in banji_list:
                    banji_list.append(new_id)
                    save_all_banji(banji_list)
                    # 创建班级文件
                    open(get_class_path(new_id), 'w').close()
                    messages.success(request, f'班级 {new_id} 添加成功')
        
        elif 'delete_banji' in request.POST:
            del_id = request.POST.get('delete_banji')
            banji_list = read_all_banji()
            if del_id in banji_list:
                banji_list.remove(del_id)
                save_all_banji(banji_list)
                if class_exists(del_id):
                    os.remove(get_class_path(del_id))
                messages.success(request, f'班级 {del_id} 已删除')
        
        return redirect('manage_banji')
    
    banji_list = sorted(read_all_banji(), key=lambda x: int(x))
    return render(request, 'banji.html', {'banji_list': banji_list})

def manage_students(request, class_id):
    """学生管理视图"""
    if not class_exists(class_id):
        messages.error(request, f'班级 {class_id} 不存在')
        return redirect('manage_banji')
    
    students = read_class_students(class_id)
    
    if request.method == 'POST':
        if 'add_student' in request.POST:
            new_name = request.POST.get('new_name')
            if new_name and new_name not in students:
                students.append(new_name)
                save_class_students(class_id, students)
                messages.success(request, f'学生 {new_name} 添加成功')
        
        elif 'delete_student' in request.POST:
            del_name = request.POST.get('delete_student')
            if del_name in students:
                students.remove(del_name)
                save_class_students(class_id, students)
                messages.success(request, f'学生 {del_name} 已删除')
        
        elif 'edit_student' in request.POST:
            old_name = request.POST.get('old_name')
            new_name = request.POST.get('new_name')
            if old_name in students and new_name:
                index = students.index(old_name)
                students[index] = new_name
                save_class_students(class_id, students)
                messages.success(request, f'学生 {old_name} 已更新为 {new_name}')
        
        return redirect('manage_students', class_id=class_id)
    
    return render(request, 'students.html', {
        'class_id': class_id,
        'students': students
    })

@login_required
def shibiema_manage(request):
    """识别码管理视图（教育管理员）"""
    if request.user.role != 'education':
        messages.error(request, '您没有权限访问此页面')
        return redirect('dashboard')
    
    schools = read_all_schools()
    shibiema_data = read_all_shibiema()
    parsed_shibiema = []
    
    for line in shibiema_data:
        parts = line.split(',')
        if len(parts) >= 3:
            parsed_shibiema.append({
                'code': parts[0],
                'school': parts[1],
                'class_name': parts[2]
            })
    
    if request.method == 'POST':
        if 'add_shibiema' in request.POST:
            school = request.POST.get('school')
            class_name = request.POST.get('class_name')
            
            if school and class_name:
                # 生成随机识别码
                import random
                import string
                code = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
                
                # 保存识别码
                shibiema_data.append(f"{code},{school},{class_name}")
                save_shibiema(shibiema_data)
                messages.success(request, f'识别码 {code} 已生成')
        
        elif 'delete_shibiema' in request.POST:
            code = request.POST.get('delete_shibiema')
            shibiema_data = [s for s in shibiema_data if not s.startswith(code + ',')]
            save_shibiema(shibiema_data)
            messages.success(request, f'识别码 {code} 已删除')
        
        return redirect('shibiema_manage')
    
    return render(request, 'education/shibiema_manage.html', {
        'shibiema_list': parsed_shibiema,
        'schools': schools
    })

@login_required
def teacher_homework_list(request):
    """教师作业管理视图"""
    if request.user.role != 'teacher':
        messages.error(request, '您没有权限访问此页面')
        return redirect('dashboard')
    
    # 获取当前教师班级的作业
    homeworks = Homework.objects.filter(
        class_name=request.user.class_name
    ).order_by('-created_at')
    
    if request.method == 'POST' and 'create_homework' in request.POST:
        subject = request.POST.get('subject')
        title = request.POST.get('title')
        content = request.POST.get('content')
        due_date = request.POST.get('due_date')
        
        if subject and title and content and due_date:
            Homework.objects.create(
                title=title,
                subject=subject,
                content=content,
                due_date=due_date,
                created_by=request.user,
                class_name=request.user.class_name
            )
            messages.success(request, '作业已发布')
            return redirect('teacher_homework_list')
    
    return render(request, 'teacher/homework_list.html', {
        'homeworks': homeworks
    })

@login_required
def teacher_timetable(request):
    """教师课程表管理视图"""
    if request.user.role != 'teacher':
        messages.error(request, '您没有权限访问此页面')
        return redirect('dashboard')
    
    class_name = request.user.class_name
    timetable = Timetable.objects.filter(class_name=class_name).order_by('day', 'period')
    
    if request.method == 'POST':
        day = request.POST.get('day')
        period = request.POST.get('period')
        subject = request.POST.get('subject')
        teacher = request.POST.get('teacher')
        
        if day and period and subject and teacher:
            # 添加新课程
            Timetable.objects.create(
                class_name=class_name,
                day=day,
                period=period,
                subject=subject,
                teacher=teacher
            )
            messages.success(request, '课程已添加')
        
        elif 'delete_course' in request.POST:
            course_id = request.POST.get('delete_id')
            try:
                course = Timetable.objects.get(id=course_id)
                course.delete()
                messages.success(request, '课程已删除')
            except Timetable.DoesNotExist:
                messages.error(request, '课程不存在')
        
        return redirect('teacher_timetable')
    
    # 按星期几组织课程表
    days = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
    day_names = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
    
    timetable_grid = {}
    for day in days:
        timetable_grid[day] = Timetable.objects.filter(
            class_name=class_name, day=day
        ).order_by('period')
    
    return render(request, 'teacher/timetable.html', {
        'timetable': timetable_grid,
        'days': days,
        'day_names': day_names
    })

@login_required
def student_dashboard(request):
    """学生控制台视图"""
    if request.user.role != 'student':
        messages.error(request, '您没有权限访问此页面')
        return redirect('dashboard')
    
    # 获取当天课程
    today = timezone.now().strftime('%a').lower()
    timetable = Timetable.objects.filter(
        class_name=request.user.class_name, day=today
    ).order_by('period')
    
    # 获取待提交作业
    pending_homeworks = Homework.objects.filter(
        class_name=request.user.class_name,
        due_date__gte=timezone.now()
    ).exclude(
        id__in=HomeworkSubmission.objects.filter(
            student=request.user
        ).values_list('homework_id', flat=True)
    )
    
    return render(request, 'student/dashboard.html', {
        'today_courses': timetable,
        'pending_homeworks': pending_homeworks
    })

@login_required
def student_homework_list(request):
    """学生作业列表视图"""
    if request.user.role != 'student':
        messages.error(request, '您没有权限访问此页面')
        return redirect('dashboard')
    
    homeworks = Homework.objects.filter(
        class_name=request.user.class_name
    ).order_by('-created_at')
    
    # 获取提交状态
    homework_status = {}
    for homework in homeworks:
        try:
            submission = HomeworkSubmission.objects.get(
                homework=homework,
                student=request.user
            )
            homework_status[homework.id] = submission.status
        except HomeworkSubmission.DoesNotExist:
            homework_status[homework.id] = 'pending'
    
    return render(request, 'student/homework_list.html', {
        'homeworks': homeworks,
        'homework_status': homework_status
    })

@login_required
def student_homework_submit(request, homework_id):
    """学生作业提交视图"""
    if request.user.role != 'student':
        messages.error(request, '您没有权限访问此页面')
        return redirect('dashboard')
    
    homework = Homework.objects.get(id=homework_id)
    try:
        submission = HomeworkSubmission.objects.get(
            homework=homework,
            student=request.user
        )
    except HomeworkSubmission.DoesNotExist:
        submission = None
    
    if request.method == 'POST':
        content = request.POST.get('content')
        
        if not submission:
            # 创建新提交
            submission = HomeworkSubmission.objects.create(
                homework=homework,
                student=request.user,
                content=content,
                status='submitted' if timezone.now() <= homework.due_date else 'late',
                submitted_at=timezone.now()
            )
            messages.success(request, '作业已提交')
        else:
            # 更新现有提交
            submission.content = content
            submission.status = 'submitted' if timezone.now() <= homework.due_date else 'late'
            submission.submitted_at = timezone.now()
            submission.save()
            messages.success(request, '作业已更新')
        
        return redirect('student_homework_list')
    
    return render(request, 'student/homework_submit.html', {
        'homework': homework,
        'submission': submission
    })