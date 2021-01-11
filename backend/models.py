from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver

class Sessionyear(models.Model):
    session_start_year = models.DateField()
    session_end_year = models.DateField()

    def __str__(self):
        return f'{self.session_start_year} - {self.session_end_year}'

class CustomUser(AbstractUser):
    user_type_data = ((1,"AdminHod"),(2,"Staff"),(3,"Student"))
    user_type = models.CharField(default=1,choices=user_type_data,max_length=40)         

class AdminHod(models.Model):
    user = models.OneToOneField(CustomUser,on_delete=models.CASCADE) 
    gender = models.CharField(default='male',max_length=40)
    profile = models.ImageField(default='static/placeholder.png',upload_to='admin_profile_pics')
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username    

class Staff(models.Model):
    user = models.OneToOneField(CustomUser,on_delete=models.CASCADE)
    gender = models.CharField(default='male',max_length=40)
    profile = models.ImageField(default='static/placeholder.png',upload_to='staff_profile_pics')
    address = models.TextField()
    fcm_token = models.TextField(default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username        


class Course(models.Model):
    course_name = models.CharField(max_length=80)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.course_name

class Student(models.Model):
    user = models.OneToOneField(CustomUser,on_delete=models.CASCADE)
    gender = models.CharField(default='male',max_length=40)
    profile = models.ImageField(default='static/placeholder.png',upload_to='student_profile_pics')
    course = models.ForeignKey(Course,on_delete=models.DO_NOTHING)
    address = models.TextField()
    fcm_token = models.TextField(default="")
    session_year = models.ForeignKey(Sessionyear,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.user.username   

class Subject(models.Model):
    subject_name = models.CharField(max_length=80)
    staff = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    course = models.ForeignKey(Course,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

class StudentResult(models.Model):
    student = models.ForeignKey(Student,on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject,on_delete=models.CASCADE)
    student_exam_result = models.FloatField(default=0)
    student_assignment_result = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

class Attendance(models.Model):
    subject = models.ForeignKey(Subject,on_delete=models.CASCADE)
    attendance_date = models.DateField()
    session_year = models.ForeignKey(Sessionyear,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

class AttendanceReport(models.Model):
    student = models.ForeignKey(Student,on_delete=models.CASCADE)
    attendance = models.ForeignKey(Attendance,on_delete=models.CASCADE)
    status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

class NotificationStudent(models.Model):
    student = models.ForeignKey(Student,on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

class NotificationStaff(models.Model):
    staff = models.ForeignKey(Staff,on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

class FeedbackStudent(models.Model):
    student = models.ForeignKey(Student,on_delete=models.CASCADE)
    feedback = models.TextField(default='')
    reply = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)    

class FeedbackStaff(models.Model):
    staff = models.ForeignKey(Staff,on_delete=models.CASCADE)
    feedback = models.TextField(default='')
    reply = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)    

class Leave_Student(models.Model):
    student = models.ForeignKey(Student,on_delete=models.CASCADE)
    leave_status = models.IntegerField(default=0)
    leave_message = models.TextField()
    leave_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True) 

class Leave_Staff(models.Model):
    staff = models.ForeignKey(Staff,on_delete=models.CASCADE)
    leave_status = models.IntegerField(default=0)
    leave_message = models.TextField()
    leave_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)         
    
@receiver(post_save,sender=CustomUser)
def create_user_profile(sender,instance,created,**kwargs):
    if created:
        if instance.user_type == 1:
            AdminHod.objects.create(user=instance)
        elif instance.user_type == 2:
            Staff.objects.create(user=instance)
        elif instance.user_type == 3:
            Student.objects.create(user=instance,course=Course.objects.get(id=1),session_year=Sessionyear.objects.get(id=1))

@receiver(post_save,sender=CustomUser)
def save_user_profile(sender,instance,**kwargs):
    if instance.user_type == 1:
        instance.adminhod.save()
    elif instance.user_type == 2:
        instance.staff.save()
    elif instance.user_type == 3:
        instance.student.save()
