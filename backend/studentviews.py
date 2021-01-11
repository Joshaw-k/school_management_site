from django.shortcuts import render,redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login,logout,authenticate
from django.contrib import messages
from django.http import HttpResponse,JsonResponse
from .models import CustomUser,Staff,Course,Subject,Student,Sessionyear,Attendance,AttendanceReport,Leave_Student,FeedbackStudent,NotificationStudent,StudentResult

def student_home(request):
    user_obj = CustomUser.objects.get(id=request.user.id)
    student = Student.objects.get(user=user_obj)
    present = AttendanceReport.objects.filter(student=student,status=True).count()
    absent = AttendanceReport.objects.filter(student=student,status=False).count()
    course_obj = student.course
    subjects = Subject.objects.filter(course=course_obj).count()
    subjects_obj = Subject.objects.filter(course=course_obj)
    total_attendance = AttendanceReport.objects.filter(student=student).count()
    present_count = []
    absent_count = []
    subject_name = []
    for subject in subjects_obj:
        subject_obj = Subject.objects.get(id=subject.id)
        attendance = Attendance.objects.filter(subject=subject_obj)
        attendance_present_count = AttendanceReport.objects.filter(attendance__in=attendance,status=True,student=student).count()
        attendance_absent_count = AttendanceReport.objects.filter(attendance__in=attendance,status=False,student=student).count()
        present_count.append(attendance_present_count)
        absent_count.append(attendance_absent_count)
        subject_name.append(subject.subject_name)
    context = {
        'total_attendance':total_attendance,
        'present':present,
        'absent':absent,
        'subjects':subjects,
        'attendance_present':present_count,
        'attendance_absent':absent_count,
        'subject_name':subject_name
    }
    return render(request,'student/student-index.html',context)

def log_in(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request,username=username,password=password)
        if user is not None:
            login(request,user)
            if user.user_type == '3':
                return redirect('student-home')
            else:
                return redirect('student-login')        
        else:
            messages.error(request,f'login details incorrect')
    else:
        pass        
    context = {
    }        
    return render(request,'student/student-login.html',context) 

def log_out(request):
    logout(request)
    return redirect('student-login')


def view_attendance(request):
    user = CustomUser.objects.get(id=request.user.id)
    course = user.student.course
    subjects = Subject.objects.filter(course=course)
    session_years = Sessionyear.objects.all()
    context = {
        'subjects':subjects,
        'session_years':session_years
    }
    return render(request,'student/student-view-attendance.html',context)                  

def view_attendance_data(request):
    subject_id = request.POST.get('subject')
    session_year_id = request.POST.get('session_year')
    user = CustomUser.objects.get(id=request.user.id)
    student = Student.objects.get(user=user)
    subjects = Subject.objects.get(id=subject_id)
    session_years = Sessionyear.objects.get(id=session_year_id)
    attendance = Attendance.objects.filter(session_year=session_years,subject=subjects)
    attendance_report = []
    for attend in attendance:
        data_small = AttendanceReport.objects.get(student=student,attendance=attend.id)
        attendance_report.append(data_small)
    attendance_report_data = []    
    for attend in attendance_report:
        data_small = {'date':str(attend.attendance.attendance_date),'status':attend.status}
        attendance_report_data.append(data_small)
    context = {
        'attendance_report_data':attendance_report_data,
        
    }
    return render(request,'student/student-view-attendance-data.html',context)  

def student_apply_leave(request):
    leave_date = request.POST.get('leave_date')
    leave_reason = request.POST.get('leave_reason')
    student_id = request.user.id
    student_obj = CustomUser.objects.get(id=student_id)
    student = Student.objects.get(user=student_obj)
    leave_status = Leave_Student.objects.filter(student=student)

    if request.method == "POST":
        try:
            leave = Leave_Student(student=student,leave_date=leave_date,leave_message=leave_reason)
            leave.save()
            messages.success(request,'sucessfully applied for leave')
            return redirect('student_apply_leave')
        except:
            messages.success(request,'failed to apply for leave')
            return redirect('student_apply_leave')
    else:
        pass    
    context = {'leave_status':leave_status}
    return render(request,'student/student_apply_leave.html', context)         

def feedback_student(request):
    feedback_message = request.POST.get('feedback_message')
    student_id = request.user.id
    student_obj = CustomUser.objects.get(id=student_id)
    student = Student.objects.get(user=student_obj)
    feedback_status = FeedbackStudent.objects.filter(student=student)
    if request.method == "POST":
        try:
            feedback = FeedbackStudent(student=student,feedback=feedback_message,reply='')
            feedback.save()
            messages.success(request,'sucessfully sent feedback')
            return redirect('feedback_student')
        except:
            messages.error(request,'failed to send feedback')
            return redirect('feedback_student')     
    else:
        pass    
    context ={'feedback_status':feedback_status}
    return render(request,'student/feedback-student.html', context)  

def student_personal_info(request):
    user_id = request.user.id
    user_obj = CustomUser.objects.get(id=user_id)
    student_obj = Student.objects.get(user=user_obj)
    context = {
        "student":student_obj
    }
    return render(request,"student/student_personal_info.html",context)     

def edit_personal_info(request):
    user_id = request.user.id
    user_obj = CustomUser.objects.get(id=user_id)
    student_obj = Student.objects.get(user=user_obj)
    if request.method == 'POST':
        email = request.POST.get('email')
        username = request.POST.get('username')
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        address = request.POST.get('address')
        try:
            user_obj.email = email
            user_obj.username = username
            user_obj.first_name = firstname
            user_obj.last_name = lastname
            user_obj.save()
            student_obj.address = address
            student_obj.save()
            messages.success(request,'sucessfully edited personal info')
            return redirect("student_personal_info")  
        except:
            messages.error(request,'failed to edit personal info') 
            return redirect("student_personal_info")     
    


@csrf_exempt
def student_fcm_token_save(request):
    token = request.POST.get("token")
    user = CustomUser.objects.get(id=request.user.id)
    student = Student.objects.get(user=user)  
    student.token = token
    student.save()
    return HttpResponse("ok")   

def student_all_notification(request):
    user = CustomUser.objects.get(id=request.user.id)
    student = Student.objects.get(user=user)
    notification = NotificationStudent.objects.filter(student=student)
    context = {"notification":notification}
    return render(request,"student/student_all_notification.html", context)    

def view_results(request):
    user = CustomUser.objects.get(id=request.user.id)
    student = Student.objects.get(user=user)
    student_results = StudentResult.objects.filter(student=student)
    context = {"student_results":student_results}
    return render(request,"student/view_results.html", context) 