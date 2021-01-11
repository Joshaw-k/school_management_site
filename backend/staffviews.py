from django.shortcuts import render,redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login,logout,authenticate
from django.contrib import messages
from .models import CustomUser,Staff,Course,Subject,Student,Sessionyear,StudentResult,Attendance,AttendanceReport,Leave_Staff,FeedbackStaff,NotificationStaff
from django.http import HttpResponse,JsonResponse
import json

def staff_home(request):
    user_obj = CustomUser.objects.get(id=request.user.id)
    staff_obj = Staff.objects.get(user=user_obj)
    subjects_obj = Subject.objects.filter(staff=user_obj)
    course_id_list = []
    for subject in subjects_obj:
        data_small = Course.objects.get(id=subject.course.id)
        course_id_list.append(data_small)   
    course_list = []
    for course in course_id_list:
        if course_list not in course_id_list:
            course_list.append(course) 
    total_students = Student.objects.filter(course__in=course_list).count() 
    total_attendance_taken = Attendance.objects.filter(subject__in=subjects_obj).count()  
    total_leave_taken = Leave_Staff.objects.filter(staff=staff_obj,leave_status=1).count
    total_subjects = Subject.objects.filter(staff=user_obj).count()     

    subject_list = []
    attended_subject_list = []
    for subject in subjects_obj:
        subject_list.append(subject.subject_name)
        attended = Attendance.objects.filter(subject=subject).count()
        attended_subject_list.append(attended) 
    student_list = []
    attendance_present = []
    attendance_absent = []
    students = Student.objects.filter(course__in=course_list)
    for student in students:
        student_list.append(student.user.username)
        attendance_present_count = AttendanceReport.objects.filter(status=True,student=student).count()
        attendance_absent_count = AttendanceReport.objects.filter(status=False,student=student).count() 
        attendance_present.append(attendance_present_count)
        attendance_absent.append(attendance_absent_count)   
    context = {
        'total_students':total_students,
        'total_attendance_taken':total_attendance_taken,
        'total_leave_taken':total_leave_taken,
        'total_subjects':total_subjects,
        'subject_list':subject_list,
        'attended_subject_list':attended_subject_list,
        'student_list':student_list,
        'attendance_present':attendance_present,
        'attendance_absent':attendance_absent
    }
    return render(request,'staff/staff-index.html',context)

def take_attendance(request):
    user = CustomUser.objects.get(id=request.user.id)
    subjects = Subject.objects.filter(staff=user)
    session_years = Sessionyear.objects.all()
    context = {
        'subjects':subjects,
        'session_years':session_years
    }
    return render(request,'staff/take-attendance.html',context)

@csrf_exempt
def get_students(request):
    subject = request.POST.get('subject_data')
    session_year = request.POST.get('session_year_data')
    subject_id = Subject.objects.get(id=subject)
    session_year_id = Sessionyear.objects.get(id=session_year)
    student = Student.objects.filter(course=subject_id.course,session_year=session_year_id)
    list_data = []
    for stud in student:
        data_small = {"id":stud.id,"name":stud.user.first_name + " " + stud.user.last_name}
        list_data.append(data_small) 
    return JsonResponse(json.dumps(list_data),content_type='application/json',safe=False)

@csrf_exempt
def save_attendance(request):
    subject = request.POST.get('subject_id')        
    session_year = request.POST.get('session_year_id')
    student_data = request.POST.get('student_data_id')
    attendance_data = request.POST.get('attendance_data_obj')
    subject_id = Subject.objects.get(id=subject)
    session_year_id = Sessionyear.objects.get(id=session_year)
    json_students = json.loads(student_data)
    try:
        attendance = Attendance(subject=subject_id,attendance_date=attendance_data,session_year=session_year_id)
        attendance.save()
        for stud in json_students:
            student_obj = Student.objects.get(id=stud['id'])
            attendancereport = AttendanceReport(student=student_obj,attendance=attendance,status=stud['status'])
            attendancereport.save()
        return HttpResponse('ok')
    except:
         return HttpResponse('error')

def view_attendance(request):
    user = CustomUser.objects.get(id=request.user.id)
    subjects = Subject.objects.filter(staff=user)
    session_years = Sessionyear.objects.all()
    context = {
        'subjects':subjects,
        'session_years':session_years
    }
    return render(request,'staff/view-attendance.html',context)

@csrf_exempt
def fetch_attendance_date(request):
    subject = request.POST.get('subject_data')
    session_year = request.POST.get('session_year_data')
    subject_obj = Subject.objects.get(id=subject)
    session_year_obj = Sessionyear.objects.get(id=session_year)
    attendance_date = Attendance.objects.filter(subject=subject_obj,session_year=session_year_obj)
    attendance_data = []
    for attendance in attendance_date:
        data_small = {"id":attendance.id,"attendance_date":str(attendance.attendance_date)}
        attendance_data.append(data_small)
    return JsonResponse(json.dumps(attendance_data),content_type='application/json',safe=False)

@csrf_exempt
def fetch_students(request):
    attendance_id = request.POST.get('attendance_date_id')
    attendance = Attendance.objects.get(id=attendance_id)
    attendancereport = AttendanceReport.objects.filter(attendance=attendance)
    attendance_data = []
    for attendance in attendancereport:
        data_small = {"id":attendance.student.id,"student":attendance.student.user.username,"status":attendance.status}
        attendance_data.append(data_small)   
    return JsonResponse(json.dumps(attendance_data),content_type='application/json',safe=False)

@csrf_exempt
def save_attendance_report(request):
    student_data = request.POST.get('student_data_id')
    attendance_date_id = request.POST.get('attendance_date_obj')
    json_students = json.loads(student_data)
    try:
        for stud in json_students:
            student_obj = Student.objects.get(id=stud['id'])
            attendance_date = Attendance.objects.get(id=attendance_date_id)
            attendancereport = AttendanceReport.objects.get(student=student_obj,attendance=attendance_date)
            attendancereport.status=stud['status']
            attendancereport.save()
        return HttpResponse('ok')
    except:
        return HttpResponse('error')    

def log_in(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request,username=username,password=password)
        if user is not None:
            login(request,user)
            if user.user_type == '2':
                return redirect('staff_home')
            else:
                return redirect('staff-login')        
        else:
            messages.error(request,f'login details incorrect')
    else:
        pass        
    context = {
    }        
    return render(request,'staff/staff-login.html',context)     

def log_out(request):
    logout(request)
    return redirect('staff-login') 

def staff_apply_leave(request):
    leave_date = request.POST.get('leave_date')
    leave_reason = request.POST.get('leave_reason')
    staff_id = request.user.id
    staff_obj = CustomUser.objects.get(id=staff_id)
    staff = Staff.objects.get(user=staff_obj)
    leave_status = Leave_Staff.objects.filter(staff=staff)
    if request.method == "POST":
        try:
            leave = Leave_Staff(staff=staff,leave_date=leave_date,leave_message=leave_reason)
            leave.save()
            messages.success(request,'sucessfully applied for leave')
            return redirect('staff_apply_leave')
        except:
            messages.error(request,'failed to apply for leave')
            return redirect('staff_apply_leave')
    else:
        pass    
    context = {'leave_status':leave_status}
    return render(request,'staff/staff_apply_leave.html', context)         

def feedback(request):
    feedback_message = request.POST.get('feedback_message')
    staff_id = request.user.id
    staff_obj = CustomUser.objects.get(id=staff_id)
    staff = Staff.objects.get(user=staff_obj)
    feedback_status = FeedbackStaff.objects.filter(staff=staff)
    if request.method == "POST":
        try:
            feedback = FeedbackStaff(staff=staff,feedback=feedback_message,reply='')
            feedback.save()
            messages.success(request,'sucessfully sent feedback')
            return redirect('feedback')
        except:
            messages.error(request,'failed to send feedback')
            return redirect('feedback')    
    else:
        pass    
    context ={'feedback_status':feedback_status}
    return render(request,'staff/feedback.html', context)  

def staff_personal_info(request):
    user_id = request.user.id
    user_obj = CustomUser.objects.get(id=user_id)
    staff_obj = Staff.objects.get(user=user_obj)
    context = {
        "staff":staff_obj
    }
    return render(request,"staff/staff_personal_info.html",context)     

def edit_personal_info(request):
    user_id = request.user.id
    user_obj = CustomUser.objects.get(id=user_id)
    staff_obj = Staff.objects.get(user=user_obj)
    if request.method == 'POST':
        email = request.POST.get('email')
        username = request.POST.get('username')
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        address = request.POST.get('address')
        try:
            user_obj.user.email = email
            user_obj.user.username = username
            user_obj.user.first_name = firstname
            user_obj.user.last_name = lastname
            user_obj.save()
            staff_obj.address = address
            staff_obj.save()
            messages.success(request,'sucessfully edited personal info')
            return redirect("staff_personal_info")
        except:
            messages.error(request,'failed to edit personal info') 
            return redirect("staff_personal_info")   
        

@csrf_exempt
def staff_fcm_token_save(request):
    token = request.POST.get("token")
    user = CustomUser.objects.get(id=request.user.id)
    staff = Staff.objects.get(user=user)  
    staff.token = token
    staff.save()
    return HttpResponse("ok")                         

def staff_all_notification(request):
    user = CustomUser.objects.get(id=request.user.id)
    staff = Staff.objects.get(user=user)
    notification = NotificationStaff.objects.filter(staff=staff)
    context = {"notification":notification}
    return render(request,"staff/staff_all_notification.html", context)

def student_result(request):
    user_obj = CustomUser.objects.get(id=request.user.id)
    subject_obj = Subject.objects.filter(staff=user_obj)
    sessionyear = Sessionyear.objects.all()
    context = {"subject_obj":subject_obj,"sessionyear":sessionyear}
    return render(request,"staff/add_student_result.html",context)

@csrf_exempt
def add_student_result(request):
    subject = request.POST.get('subject_data')
    session_year = request.POST.get('session_year_data')
    subject_obj = Subject.objects.get(id=subject)
    session_year_obj = Sessionyear.objects.get(id=session_year)
    students = Student.objects.filter(course=subject_obj.course,session_year=session_year_obj)
    student_data = []
    for student in students:
        data_small = {"ID":student.id,"student_name":student.user.username}
        student_data.append(data_small)
    print(student_data)
    return JsonResponse(json.dumps(student_data),content_type='application/json',safe=False)

@csrf_exempt
def save_student_result(request):
    subject_id = request.POST.get("subject")
    student_id = request.POST.get("student_name")
    assignment_marks = request.POST.get("assignment_marks")
    exam_marks = request.POST.get("exam_marks")
    subject_obj = Subject.objects.get(id=subject_id)
    student_obj = Student.objects.get(id=student_id)
    check_exists = StudentResult.objects.filter(student=student_obj,subject=subject_obj).exists()
    if check_exists:
        result = StudentResult.objects.get(student=student_obj,subject=subject_obj)
        result.student_exam_result = exam_marks
        result.student_assignment_result = assignment_marks
        result.save()
        return redirect("student_result")
    else:    
        result = StudentResult(student=student_obj,subject=subject_obj,student_exam_result=exam_marks,student_assignment_result=assignment_marks)
        result.save()
        return redirect("student_result")

def edit_student_result(request):
    staff = CustomUser.objects.get(id=request.user.id)
    subjects = Subject.objects.filter(staff=staff)
    session_years = Sessionyear.objects.all()
    context = {
        "subjects":subjects,
        "session_years":session_years
        }
    return render(request,"staff/edit_student_result.html",context) 

@csrf_exempt
def get_student_for_result(request):
    subject = request.POST.get('subject_data')
    session_year = request.POST.get('session_year_data')
    subject_obj = Subject.objects.get(id=subject)
    session_year_obj = Sessionyear.objects.get(id=session_year)
    students = Student.objects.filter(course=subject_obj.course,session_year=session_year_obj)
    student_data = []
    for student in students:
        data_small = {"ID":student.id,"student_name":student.user.username}
        student_data.append(data_small)
    return JsonResponse(json.dumps(student_data),content_type='application/json',safe=False) 

@csrf_exempt
def fetch_student_result(request):
    subject = request.POST.get('subject_data')
    student_id = request.POST.get("student_obj")
    subject_obj = Subject.objects.get(id=subject)
    student = Student.objects.get(id=student_id)
    result = StudentResult.objects.get(student=student,subject=subject_obj)
    result_obj = {"assignment_mark":result.student_assignment_result,"exam_mark":result.student_exam_result}
    return JsonResponse(json.dumps(result_obj),content_type='application/json',safe=False)

@csrf_exempt
def save_edited_student_result(request):
    subject_id = request.POST.get("subject_data")
    student_id = request.POST.get("student_obj")
    assignment_marks = request.POST.get("assignment_mark")
    exam_marks = request.POST.get("exam_mark")
    subject_obj = Subject.objects.get(id=subject_id)
    student_obj = Student.objects.get(id=student_id)
    result = StudentResult.objects.get(student=student_obj,subject=subject_obj)
    result.student_exam_result = exam_marks
    result.student_assignment_result = assignment_marks
    result.save()
    return HttpResponse("Student result has been saved") 