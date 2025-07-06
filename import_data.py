import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "roll_call.settings")  # 替换为你的项目名
django.setup()

from call.models import Banji, Student  # 替换为你的应用名

def import_banji_and_students():
    # 读取 banji.txt 文件
    banji_file_path = os.path.join(os.getcwd(), "banji.txt")
    with open(banji_file_path, "r", encoding="utf-8") as f:
        banji_ids = [line.strip() for line in f if line.strip()]

    # 遍历每个班级编号
    for class_id in banji_ids:
        student_file_path = os.path.join(os.getcwd(), f"{class_id}.txt")
        if not os.path.exists(student_file_path):
            print(f"文件 {student_file_path} 不存在，跳过班级 {class_id}")
            continue

        # 创建班级
        banji, created = Banji.objects.get_or_create(
            class_id=class_id,
            defaults={"class_name": f"班级 {class_id}"}
        )
        if created:
            print(f"创建班级 {class_id}")
        else:
            print(f"班级 {class_id} 已存在")

        # 读取学生名单
        with open(student_file_path, "r", encoding="utf-8") as f:
            students = [line.strip() for line in f if line.strip()]

        # 批量创建学生
        student_objects = [
            Student(name=name, class_id=banji) for name in students
        ]
        Student.objects.bulk_create(student_objects)
        print(f"班级 {class_id} 的 {len(students)} 名学生已导入")

if __name__ == "__main__":
    import_banji_and_students()