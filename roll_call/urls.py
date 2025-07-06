# roll_call/urls.py
from django.contrib import admin
from django.urls import path
from call.views import (
    manage_banji, 
    manage_students, 
    index, 
    attendance_statistics,
    user_login, 
    user_logout,
    role_select,
    register,
    dashboard,
    shibiema_manage,
    teacher_homework_list,
    teacher_timetable,
    student_dashboard,
    student_homework_list,
    student_homework_submit
)

urlpatterns = [
    path('banji/', manage_banji, name='manage_banji'),
    path('students/<str:class_id>/', manage_students, name='manage_students'),
    path("admin/", admin.site.urls),
    path("", index, name="index"),
    path("jilu/", attendance_statistics, name="attendance_statistics"),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('role_select/', role_select, name='role_select'),
    path('register/', register, name='register'),
    path('dashboard/', dashboard, name='dashboard'),
    path('shibiema_manage/', shibiema_manage, name='shibiema_manage'),
    path('teacher/homework_list/', teacher_homework_list, name='teacher_homework_list'),
    path('teacher/timetable/', teacher_timetable, name='teacher_timetable'),
    path('student/dashboard/', student_dashboard, name='student_dashboard'),
    path('student/homework_list/', student_homework_list, name='student_homework_list'),
    path('student/homework_submit/<int:homework_id>/', student_homework_submit, name='student_homework_submit'),
]