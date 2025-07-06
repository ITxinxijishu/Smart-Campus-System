from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import School
from .file_utils import save_school, read_all_schools, save_shibiema, read_all_shibiema

@login_required
def school_manage(request):
    if request.user.role != 'education':
        return redirect('dashboard')
    
    schools = read_all_schools()
    
    if request.method == 'POST':
        school_name = request.POST.get('school_name')
        if school_name:
            # 保存学校
            schools.append(school_name)
            save_school(schools)
            messages.success(request, '学校添加成功')
        return redirect('school_manage')
    
    return render(request, 'education/school_manage.html', {'schools': schools})

@login_required
def shibiema_manage(request):
    if request.user.role != 'education':
        return redirect('dashboard')
    
    shibiema_data = read_all_shibiema()
    schools = read_all_schools()
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
            messages.success(request, '识别码已删除')
        
        return redirect('shibiema_manage')
    
    return render(request, 'education/shibiema_manage.html', {
        'shibiema_list': parsed_shibiema,
        'schools': schools
    })