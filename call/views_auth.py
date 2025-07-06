from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User, Shibiema
from .file_utils import save_shibiema, read_all_shibiema

def role_select(request):
    if request.method == 'POST':
        request.session['register_role'] = request.POST.get('role')
        return redirect('register')
    return render(request, 'auth/role_select.html')

def register(request):
    role = request.session.get('register_role', 'student')
    
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
    
    return render(request, 'auth/register.html', {'role': role})

def user_login(request):
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
    logout(request)
    return redirect('index')

@login_required
def dashboard(request):
    user = request.user
    if user.role == 'education':
        return redirect('school_manage')
    elif user.role == 'teacher':
        return redirect('teacher_homework_list')
    elif user.role == 'student':
        return redirect('student_homework_list')
    return redirect('index')