from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Homework, HomeworkSubmission, Timetable
from .file_utils import get_timetable_path, read_timetable

@login_required
def homework_list(request):
    if request.user.role != 'student':
        return redirect('dashboard')
    
    # 获取当前学生的所有作业
    homeworks = Homework.objects.filter(
        class_name=request.user.class_name
    ).order_by('-created_at')
    
    # 获取学生的作业提交状态
    homework_status = {}
    for homework in homeworks:
        submission = HomeworkSubmission.objects.filter(
            homework=homework,
            student=request.user
        ).first()
        
        if submission:
            homework_status[homework.id] = submission.status
        else:
            homework_status[homework.id] = 'pending'
    
    return render(request, 'student/homework_list.html', {
        'homeworks': homeworks,
        'homework_status': homework_status
    })

@login_required
def homework_submit(request, homework_id):
    if request.user.role != 'student':
        return redirect('dashboard')
    
    homework = get_object_or_404(Homework, id=homework_id)
    submission = HomeworkSubmission.objects.filter(
        homework=homework,
        student=request.user
    ).first()
    
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

@login_required
def student_dashboard(request):
    if request.user.role != 'student':
        return redirect('dashboard')
    
    # 获取当天课程表
    import datetime
    today = datetime.datetime.now().strftime('%a').lower()
    timetable_data = read_timetable(request.user.class_name)
    
    today_courses = []
    for line in timetable_data:
        parts = line.split(',')
        if len(parts) >= 4 and parts[0] == today:
            today_courses.append({
                'period': parts[1],
                'subject': parts[2],
                'teacher': parts[3]
            })
    
    # 获取待提交作业
    pending_homeworks = []
    homeworks = Homework.objects.filter(
        class_name=request.user.class_name,
        due_date__gte=timezone.now()
    )
    
    for homework in homeworks:
        submission = HomeworkSubmission.objects.filter(
            homework=homework,
            student=request.user
        ).first()
        
        if not submission or submission.status == 'pending':
            pending_homeworks.append(homework)
    
    return render(request, 'student/dashboard.html', {
        'today_courses': today_courses,
        'pending_homeworks': pending_homeworks
    })