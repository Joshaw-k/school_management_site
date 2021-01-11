from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser,AdminHod,Staff,Student,Course,Subject,Attendance,AttendanceReport,NotificationStaff,NotificationStudent,FeedbackStaff,FeedbackStudent,Leave_Staff,Leave_Student

class UserModel(UserAdmin):
    pass

admin.site.register(CustomUser,UserAdmin)
# admin.site.register(Gender)
admin.site.register(AdminHod)
admin.site.register(Staff)
admin.site.register(Student)
admin.site.register(Course)
admin.site.register(Subject)
admin.site.register(Attendance)
admin.site.register(AttendanceReport)
admin.site.register(NotificationStaff)
admin.site.register(NotificationStudent)
admin.site.register(FeedbackStaff)
admin.site.register(FeedbackStudent)
admin.site.register(Leave_Staff)
admin.site.register(Leave_Student)