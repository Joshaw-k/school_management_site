from django.shortcuts import render,redirect
from django.contrib.auth import login,logout,authenticate
from django.contrib import messages
from .models import CustomUser,Staff,Course,Subject,Student,Sessionyear,FeedbackStaff,FeedbackStudent,Leave_Student,Leave_Staff,Attendance,AttendanceReport,NotificationStudent,NotificationStaff
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse,JsonResponse
import json
import requests

def admin_home(request):
    students = Student.objects.all().count()
    staffs = Staff.objects.all().count()
    courses = Course.objects.all().count()
    subjects = Subject.objects.all().count()

    course_list = []
    subject_list = []
    student_list = []
    courses_obj = Course.objects.all()
    for course in courses_obj:
        course_list.append(course.course_name)
        subject_no = Subject.objects.filter(course=course).count()
        student_no = Student.objects.filter(course=course).count()
        subject_list.append(subject_no)
        student_list.append(student_no) 

    subject_list_2 = []
    student_list_2 = []
    subjects_obj = Subject.objects.all()
    for subject in subjects_obj:
        subject_list_2.append(subject.subject_name)
        student_no = Student.objects.filter(course=subject.course).count()
        student_list_2.append(student_no)

    staff_list = []
    attendance_staff = []
    leave_staff = []   
    staffs_obj = Staff.objects.all()
    for staff in staffs_obj:
        staff_list.append(staff.user.username)
        subject_id = Subject.objects.filter(staff=staff.user)
        attendance = Attendance.objects.filter(subject__in=subject_id).count()
        leave = Leave_Staff.objects.filter(staff=staff).count()
        attendance_staff.append(attendance)
        leave_staff.append(leave)   

    student_list_3 = []
    attendance_staff_2 = []
    leave_staff_2 = []   
    students_obj = Student.objects.all()
    for student in students_obj:
        student_list_3.append(student.user.username)
        attendance = AttendanceReport.objects.filter(student=student,status=True).count()
        leave = Leave_Student.objects.filter(student=student).count()
        attendance_staff_2.append(attendance)
        leave_staff_2.append(leave)    
    context = {
        'students':students,
        'staffs':staffs,
        'courses':courses,
        'subjects':subjects,
        'course_list':course_list,
        'subject_list':subject_list,
        'student_list':student_list,
        'subject_list_2':subject_list_2,
        'student_list_2':student_list_2,
        'staff_list':staff_list,
        'attendance_staff':attendance_staff,
        'leave_staff':leave_staff,
        'student_list_3':student_list_3,
        'attendance_staff_2':attendance_staff_2,
        'leave_staff_2':leave_staff_2
    }
    return render(request,'adminhod/admin-index.html',context)    

def log_in(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request,username=username,password=password)
        if user is not None:
            login(request,user)
            if user.user_type == '1':
                return redirect('admin_home')
            else:
                return redirect('home')        
        else:
            messages.error(request,f'login details incorrect')
    else:
        pass        
    context = {
    }        
    return render(request,'adminhod/admin-login.html',context) 

def log_out(request):
    logout(request)
    return redirect('admin-login')  

def add_staff(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        username = request.POST.get('username')
        address = request.POST.get('address')
        try:
            user = CustomUser.objects.create_user(username=username, email=email, password=password,first_name=firstname,last_name=lastname,user_type=2)
            user.staff.address = address
            user.save()
            messages.success(request,f"sucessfully added {username}'s details")
            return redirect('add-staff')
        except:
            messages.error(request,f"failed to add {username}'s details")
            return redirect('add-staff')

    return render(request,'adminhod/add_staff.html')         

def add_course(request):
    if request.method == "POST":
        courses = request.POST.get('course')
        try:
            course = Course.objects.create(course_name=courses)
            course.save()
            messages.success(request,f'sucessfully added {courses}')
            return redirect('add-course')
        except:
            messages.error(request,f'failed to add {courses}')
            return redirect('add-course')      

    return render(request,'adminhod/add_course.html') 

def manage_course(request):
    courses = Course.objects.all()
    context = {
        'courses':courses
    }
    return render(request,'adminhod/manage-course.html',context)                         

def edit_course(request,id):
    courses = Course.objects.get(id=id)
    if request.method == "POST":
        course = request.POST.get('course')
        try:
            courses.course_name = course
            courses.save()
            messages.success(request,f'sucessfully edited {course}')
            return redirect('edit-course',id)
        except:
            messages.error(request,f'failed to edit {course}')
            return redirect('edit-course',id)    

    return render(request,'adminhod/edit_course.html',{'course':courses,'id':id})         

def add_subject(request):
    courses = Course.objects.all()
    staffs = CustomUser.objects.filter(user_type=2)
    if request.method == "POST":
        courses = request.POST.get('course')
        subject = request.POST.get('subject')
        staff = request.POST.get('staff')
        course = Course.objects.get(id=courses)
        staff_obj = CustomUser.objects.get(id=staff)
        try:
            subjects = Subject.objects.create(subject_name=subject,course=course,staff=staff_obj)
            subjects.save()
            messages.success(request,f'sucessfully added {subject}')
            return redirect('add-subject')
        except:
            messages.error(request,f'failed to add {subject}')
            return redirect('add-subject')    
    context = {
        'courses':courses,
        'staffs':staffs
    }
    return render(request,'adminhod/add-subject.html',context)             

def manage_subject(request):
    subjects = Subject.objects.all()
    context = {
        'subjects':subjects
    }
    return render(request,'adminhod/manage-subject.html',context)             

def edit_subject(request,id):
    subjects = Subject.objects.get(id=id)
    courses = Course.objects.all()
    staffs = CustomUser.objects.filter(user_type=2)
    if request.method == "POST":
        courses = request.POST.get('course')
        subject = request.POST.get('subject')
        staff = request.POST.get('staff')
        try:
            course = Course.objects.get(id=courses)
            staffs = CustomUser.objects.get(id=staff)
            subjects.subject_name = subject
            subjects.staff = staffs
            subjects.course = course
            subjects.save()
            messages.success(request,f'sucessfully added {subject}')
            return redirect('edit-subject',id)
        except: 
            messages.error(request,f'failed to edit {subject}')
            return redirect('edit-subject',id)   
    context = {
        'courses':courses,
        'staffs':staffs,
        'subject':subjects,
        'id':id
    }
    return render(request,'adminhod/edit-subject.html',context)             

def add_student(request):
    courses = Course.objects.all()
    sessions = Sessionyear.objects.all()
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        username = request.POST.get('username')
        address = request.POST.get('address')
        gender = request.POST.get('gender')
        course = request.POST.get('course')
        session_year = request.POST.get('session-year')
        try:
            user = CustomUser.objects.create_user(username=username, email=email, password=password,first_name=firstname,last_name=lastname,user_type=3)
            user.student.address = address
            user.student.gender = gender
            course_obj = Course.objects.get(id=course)
            session_year_obj = Sessionyear.objects.get(id=session_year)
            user.student.session_year = session_year_obj
            user.student.course = course_obj
            user.save()
            messages.success(request,f"sucessfully added {username}'s details")
            return redirect('add-student')
        except:
            messages.error(request,f"failed to add {username}'s details")
            return redirect('add-student')   

    return render(request,'adminhod/add-student.html',{'courses':courses,'sessions':sessions})   

def manage_staff(request):
    staffs = Staff.objects.all()
    return render(request,'adminhod/manage-staff.html',{'staffs':staffs})    

def edit_staff(request,id):
    staff = Staff.objects.get(id=id)
    if request.method == "POST":
        email = request.POST.get('email')
        firstname = request.POST.get('firstname') 
        lastname = request.POST.get('lastname')
        username = request.POST.get('username')
        address = request.POST.get('address')
        staff_id = request.POST.get('staff_id')
        gender = request.POST.get('gender')
        try:
            users = CustomUser.objects.get(id=staff_id)
            users.email = email
            users.first_name = firstname
            users.last_name = lastname
            users.username = username
            users.save()
            staff.address = address
            staff.gender = gender
            staff.save()
            messages.success(request,'sucessfully edited staff details')
            return redirect('edit-staff',id)
        except:
            messages.error(request,'failed to edit staff details')
            return redirect('edit-staff',id)    

    return render(request,'adminhod/edit-staff.html',{'staff':staff,'id':id})

def manage_student(request):
    students = Student.objects.all()
    return render(request,'adminhod/manage-student.html',{'students':students})  

def edit_student(request,id):
    courses = Course.objects.all()
    student = Student.objects.get(id=id)
    sessions = Sessionyear.objects.all()
    if request.method == "POST":
        email = request.POST.get('email')
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        username = request.POST.get('username')
        address = request.POST.get('address')
        student_id = request.POST.get('student_id')
        course = request.POST.get('course')
        session_year = request.POST.get('session-year')
        try:
            session_year_obj = Sessionyear.objects.get(id=session_year)
            course_obj = Course.objects.get(id=course)
            user = CustomUser.objects.get(id=student_id)
            user.email = email
            user.first_name = firstname
            user.last_name = lastname
            user.username = username
            user.save()
            student.address = address
            student.course = course_obj
            student.session_year = session_year_obj
            student.save()
            messages.success(request,'sucessfully edited student details')
            return redirect('edit-student',id)
        except:    
            messages.error(request,'failed to edit student details')
            return redirect('edit-student',id)
    context = {
        'student':student,
        'courses':courses,
        'id':id,
        'sessions':sessions
    }
    return render(request,'adminhod/edit-student.html',context) 

def manage_session(request):
    if request.method == 'POST':
        session_start = request.POST.get('session-start-year')
        session_end = request.POST.get('session-end-year')
        try:
            session = Sessionyear(session_start_year=session_start,session_end_year=session_end)
            session.save()
            messages.success(request,'sucessfully added session year')
            return redirect('manage-session')
        except:
            messages.error(request,'failed to add session year')
            return redirect('manage-session')     
    context = {}
    return render(request,'adminhod/manage-session.html',context)  

@csrf_exempt
def check_email_exists(request):
    email = request.POST.get('email')
    emai_obj = CustomUser.objects.filter(email=email).exists()
    if emai_obj:
        return HttpResponse(True)                       
    else:
        return HttpResponse(False)                           

@csrf_exempt
def check_username_exists(request):
    username = request.POST.get('username')
    username_obj = CustomUser.objects.filter(username=username).exists()
    if username_obj:
        return HttpResponse(True)                       
    else:
        return HttpResponse(False) 

def staff_message_reply(request):
    feedbacks = FeedbackStaff.objects.all()
    context = {'feedbacks':feedbacks}
    return render(request,"adminhod/staff-message-reply.html",context)                                  

@csrf_exempt
def staff_message_reply_get(request):
    feedback_id = request.POST.get('id')
    feedback_message = request.POST.get('message')

    feedback_obj = FeedbackStaff.objects.get(id=feedback_id)
    feedback_obj.reply = feedback_message
    feedback_obj.save() 
    return HttpResponse('ok')                                  

def student_message_reply(request):
    feedbacks = FeedbackStudent.objects.all()
    context = {'feedbacks':feedbacks}
    return render(request,"adminhod/student-message-reply.html",context)                                  

@csrf_exempt
def student_message_reply_get(request):
    feedback_id = request.POST.get('id')
    feedback_message = request.POST.get('message')

    feedback_obj = FeedbackStudent.objects.get(id=feedback_id)
    feedback_obj.reply = feedback_message
    feedback_obj.save() 
    return HttpResponse('ok')

def student_leave(request):
    leave = Leave_Student.objects.all()
    context = {'leave_status':leave}
    return render(request,"adminhod/student-leave.html",context)                                  

def student_leave_approve(request,id):
    leave = Leave_Student.objects.get(id=id)
    leave.leave_status = 1
    leave.save()
    return redirect("student_leave")

def student_leave_reject(request,id):
    leave = Leave_Student.objects.get(id=id)
    leave.leave_status = 2
    leave.save()
    return redirect("student_leave")

def staff_leave(request):
    leave = Leave_Staff.objects.all()
    context = {'leave_status':leave}
    return render(request,"adminhod/staff-leave.html",context)                                  

def staff_leave_approve(request,id):
    leave = Leave_Staff.objects.get(id=id)
    leave.leave_status = 1
    leave.save()
    return redirect("staff_leave")

def staff_leave_reject(request,id):
    leave = Leave_Staff.objects.get(id=id)
    leave.leave_status = 2
    leave.save()
    return redirect("staff_leave")

def admin_personal_info(request):
    user_id = request.user.id
    user_obj = CustomUser.objects.get(id=user_id)
    context = {
        "user":user_obj
    }
    return render(request,"adminhod/admin-personal-info.html",context)     

def edit_personal_info(request):
    user_id = request.user.id
    user_obj = CustomUser.objects.get(id=user_id)

    if request.method == 'POST':
        email = request.POST.get('email')
        username = request.POST.get('username')
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        try:
            user_obj.email = email
            user_obj.username = username
            user_obj.first_name = firstname
            user_obj.last_name = lastname
            user_obj.save()
            messages.success(request,'sucessfully edited personal info')
            return redirect("admin_personal_info")
        except:
            messages.error(request,'failed to edit personal info')
            return redirect("admin_personal_info")    
     

def send_staff_notification(request):
    staffs = Staff.objects.all()
    context = {"staffs":staffs}
    return render(request,"adminhod/staff-notification.html",context)         

def send_student_notification(request):
    students = Student.objects.all()
    context = {"students":students}
    return render(request,"adminhod/student-notification.html",context)   

@csrf_exempt
def send_student_message(request):
    user_id = request.POST.get("student_id")
    message = request.POST.get("message")
    user_obj = CustomUser.objects.get(id=user_id)
    student_obj = Student.objects.get(user=user_obj)
    token = student_obj.fcm_token
    url="https://fcm.googleapis.com/fcm/send"
    body={
        "notification":{
            "title":"School Management System",
            "body":message,
            "click_action": "{% url 'student_all_notification' %}",
            "icon": ""
        },
        "to":token
    }
    headers={"Content-Type":"application/json","Authorization":"key=AAAAJXLxDwE:APA91bGRULKqZ_RrNnQ_8AbI3OqJvbrbpBX7X_-tid9QxUP1fdTSFLqg107_QxgQpIaal5WeAyoSaZjcCqkL7V6xAgPdvqDpltKoD52ZpYi9KRWiqKNcX7W-gcUmJDqk-4RREmaVamwY"}
    data=requests.post(url,data=json.dumps(body),headers=headers)
    notification = NotificationStudent(student=student_obj,message=message)
    notification.save()
    print(data.text)
    return HttpResponse("ok")

@csrf_exempt
def send_staff_message(request):
    user_id = request.POST.get("staff_id")
    message = request.POST.get("message")
    user_obj = CustomUser.objects.get(id=user_id)
    staff_obj = Staff.objects.get(user=user_obj)
    token = staff_obj.fcm_token
    url="https://fcm.googleapis.com/fcm/send"
    body={
        "notification":{
            "title":"School Management System",
            "body":message,
            "click_action": "{% url 'staff_all_notification' %}",
            "icon": ""
        },
        "to":token
    }
    headers={"Content-Type":"application/json","Authorization":"key=AAAAJXLxDwE:APA91bGRULKqZ_RrNnQ_8AbI3OqJvbrbpBX7X_-tid9QxUP1fdTSFLqg107_QxgQpIaal5WeAyoSaZjcCqkL7V6xAgPdvqDpltKoD52ZpYi9KRWiqKNcX7W-gcUmJDqk-4RREmaVamwY"}
    data=requests.post(url,data=json.dumps(body),headers=headers)
    notification = NotificationStaff(staff=staff_obj,message=message)
    notification.save()
    return HttpResponse("ok")    