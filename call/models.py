from django.db import models
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

class User(AbstractUser):
    ROLE_CHOICES = (
        ('education', '教育管理员'),
        ('teacher', '教师'),
        ('student', '学生'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    school_code = models.CharField(max_length=20, blank=True, null=True)
    class_name = models.CharField(max_length=50, blank=True, null=True)
    real_name = models.CharField(max_length=50, blank=True, null=True)

    # 添加自定义的反向关联名称
    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        help_text='用户所属的所有组',
        related_name="custom_user_set",  # 添加这行
        related_query_name="custom_user",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        help_text='用户的所有权限',
        related_name="custom_user_set",  # 添加这行
        related_query_name="custom_user",
    )
class School(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Shibiema(models.Model):
    code = models.CharField(max_length=20, unique=True)
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    class_name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

class Homework(models.Model):
    title = models.CharField(max_length=200)
    subject = models.CharField(max_length=50)
    content = models.TextField()
    due_date = models.DateTimeField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    class_name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

class HomeworkSubmission(models.Model):
    homework = models.ForeignKey(Homework, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    STATUS_CHOICES = (
        ('pending', '待提交'),
        ('submitted', '已提交'),
        ('late', '迟交'),
        ('graded', '已批改'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    submitted_at = models.DateTimeField(null=True, blank=True)
    grade = models.CharField(max_length=20, blank=True, null=True)
    feedback = models.TextField(blank=True, null=True)
    
class Timetable(models.Model):
    DAY_CHOICES = (
        ('mon', '星期一'),
        ('tue', '星期二'),
        ('wed', '星期三'),
        ('thu', '星期四'),
        ('fri', '星期五'),
        ('sat', '星期六'),
        ('sun', '星期日'),
    )
    class_name = models.CharField(max_length=50)
    day = models.CharField(max_length=10, choices=DAY_CHOICES)
    period = models.IntegerField()
    subject = models.CharField(max_length=50)
    teacher = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

class Attendance(models.Model):
    student_name = models.CharField(max_length=100, verbose_name="学生姓名")
    class_name = models.CharField(max_length=100, verbose_name="班级名称")
    timestamp = models.DateTimeField(default=timezone.now, verbose_name="点名时间")

    def __str__(self):
        return f"{self.class_name} - {self.student_name} ({self.timestamp})"

    class Meta:
        indexes = [
            models.Index(fields=["student_name"]),
            models.Index(fields=["class_name", "student_name"]),
        ]