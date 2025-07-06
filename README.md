# Smart Campus System - 校园智能管理系统

## 项目概述

Smart Campus System 是一个基于 Django 的校园智能管理系统，集成了随机点名、班级管理、课程管理、作业管理等功能，旨在为学校提供全方位的数字化管理解决方案。

## 系统功能

### 核心功能
- **随机点名系统**：公平算法确保每个学生被点到的机会均等
- **班级管理**：班级创建、学生管理、识别码生成
- **课程管理**：课程表创建、课程安排、教师分配
- **作业管理**：作业发布、提交、批改与反馈

### 用户角色
1. **教育管理员**：
   - 管理学校与班级
   - 生成班级识别码
   - 查看全校数据统计

2. **教师**：
   - 管理班级学生
   - 发布和批改作业
   - 创建课程表
   - 使用随机点名功能

3. **学生**：
   - 查看课程安排
   - 提交作业
   - 查看成绩和反馈

## 项目结构

```
smart_campus/
├── call/                  # 核心应用
│   ├── migrations/        # 数据库迁移文件
│   ├── templates/         # 模板文件
│   ├── admin.py           # 管理员配置
│   ├── apps.py            # 应用配置
│   ├── models.py          # 数据模型
│   ├── views.py           # 视图函数
│   └── ...                # 其他文件
├── smart_campus/          # 项目配置
│   ├── settings.py        # 项目设置
│   ├── urls.py            # URL路由
│   └── ...                # 其他配置
├── data/                  # 数据文件
├── templates/             # 全局模板
├── static/                # 静态文件
├── manage.py              # Django管理脚本
├── README.md              # 项目文档
└── requirements.txt       # 依赖列表
```

## 班级数据

系统包含10个班级的学生名单：

| 班级文件 | 学生数量 |
|----------|----------|
| `1.txt`  | 36名学生 |
| `2.txt`  | 35名学生 |
| `3.txt`  | 36名学生 |
| `4.txt`  | 34名学生 |
| `5.txt`  | 36名学生 |
| `6.txt`  | 36名学生 |
| `7.txt`  | 34名学生 |
| `8.txt`  | 35名学生 |
| `9.txt`  | 36名学生 |
| `10.txt` | 34名学生 |
......

## 技术栈

- **后端框架**：Django 4.2
- **前端**：Bootstrap 5, Font Awesome
- **数据库**：SQLite (开发环境)，支持PostgreSQL/MySQL
- **部署**：Docker容器化部署
- **其他**：Redis缓存，Celery异步任务

## 安装与运行

### 环境要求
- Python 3.9+
- Django 4.2

### 安装步骤
```bash
# 克隆仓库
git clone https://github.com/yourusername/smart_campus.git

# 进入项目目录
cd smart_campus

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate    # Windows

# 安装依赖
pip install -r requirements.txt

# 应用数据库迁移
python manage.py migrate

# 创建超级用户
python manage.py createsuperuser

# 运行开发服务器
python manage.py runserver
```

## 使用指南

1. **访问系统**：http://localhost:8000
2. **角色选择**：
   - 教育管理员：管理学校和班级
   - 教师：管理课程和作业
   - 学生：查看课程和提交作业
3. **主要功能**：
   - 随机点名：选择班级后点击"开始随机点名"
   - 班级管理：添加/删除班级和学生
   - 作业管理：教师发布作业，学生提交
   - 课程管理：创建课程表

## 系统界面

### 随机点名界面
![点名界面](https://via.placeholder.com/800x400?text=Random+Roll+Call+Interface)

### 班级管理
![班级管理](https://via.placeholder.com/800x400?text=Class+Management)

### 作业管理
![作业管理](https://via.placeholder.com/800x400?text=Homework+Management)

## 开发计划

### V1.0 (已完成)
- 班级管理系统
- 随机点名功能
- 基础用户系统

### V2.0 (开发中)
- 课程表管理系统
- 作业发布与提交功能
- 点名统计与分析

### V3.0 (规划中)
- 校园通知系统
- 在线考试功能
- 移动端适配
