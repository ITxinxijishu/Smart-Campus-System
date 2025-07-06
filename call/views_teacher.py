from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Homework, HomeworkSubmission, Timetable
from .file_utils import get_timetable_path, save_timetable, read_timetable

@login_required
def homework_create(request):
    if request.user.role != 'teacher':
        return redirect('dashboard')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        subject = request.POST.get('subject')
        content = request.POST.get('content')
        due_date = request.POST.get('due_date')
        
        if title and subject and content and due_date:
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
    
    return render(request, 'teacher/homework_create.html')

@login_required
def homework_list(request):
    if request.user.role != 'teacher':
        return redirect('dashboard')
    
    homeworks = Homework.objects.filter(
        class_name=request.user.class_name
    ).order_by('-created_at')
    
    return render(request, 'teacher/homework_list.html', {'homeworks': homeworks})

@login_required
def homework_detail(request, homework_id):
    if request.user.role != 'teacher':
        return redirect('dashboard')
    
    homework = get_object_or_404(Homework, id=homework_id)
    submissions = HomeworkSubmission.objects.filter(
        homework=homework
    ).select_related('student')
    
    if request.method == 'POST':
        for submission in submissions:
            grade = request.POST.get(f'grade_{submission.id}')
            feedback = request.POST.get(f'feedback_{submission.id}')
            status = request.POST.get(f'status_{submission.id}')
            
            if grade and feedback and status:
                submission.grade = grade
                submission.feedback = feedback
                submission.status = status
                submission.save()
        
        messages.success(request, '批改结果已保存')
        return redirect('homework_detail', homework_id=homework_id)
    
    return render(request, 'teacher/homework_detail.html', {
        'homework': homework,
        'submissions': submissions
    })

@login_required
def timetable_manage(request):
    if request.user.role != 'teacher':
        return redirect('dashboard')
    
    class_name = request.user.class_name
    timetable_data = read_timetable(class_name)
    
    if request.method == 'POST':
        day = request.POST.get('day')
        period = request.POST.get('period')
        subject = request.POST.get('subject')
        teacher = request.POST.get('teacher')
        
        if day and period and subject and teacher:
            # 添加新课程
            timetable_data.append(f"{day},{period},{subject},{teacher}")
            save_timetable(class_name, timetable_data)
            messages.success(request, '课程已添加')
        
        elif 'delete_course' in request.POST:
            index = int(request.POST.get('delete_index'))
            if 0 <= index < len(timetable_data):
                del timetable_data[index]
                save_timetable(class_name, timetable_data)
                messages.success(request, '课程已删除')
        
        return redirect('timetable_manage')
    
    # 解析课程表数据
    parsed_timetable = []
    for i, line in enumerate(timetable_data):
        parts = line.split(',')
        if len(parts) >= 4:
            parsed_timetable.append({
                'index': i,
                'day': parts[0],
                'period': parts[1],
                'subject': parts[2],
                'teacher': parts[3]
            })
    
    return render(request, 'teacher/timetable.html', {
        'timetable': parsed_timetable
    })