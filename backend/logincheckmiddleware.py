from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import render,redirect
from django.urls import reverse

class LoginCheckMiddleWare(MiddlewareMixin):

    def process_view(self,request,view_func,view_args,view_kwargs):
        modulename = view_func.__module__
        user = request.user

        if user.is_authenticated:
            if user.user_type == '1':
                if modulename == 'backend.hodviews':
                    pass
                elif modulename == 'backend.views' or modulename == 'django.views.static':
                    pass
                else:
                    return redirect('admin_home')

            elif user.user_type == '2':
                if modulename == 'backend.staffviews':
                    pass 
                elif modulename == 'backend.views' or modulename == 'django.views.static':
                    pass
                else:
                    return redirect('staff_home')

            elif user.user_type == '3':
                if modulename == 'backend.studentviews':
                    pass
                elif modulename == 'backend.views' or modulename == 'django.views.static':
                    pass
                else:
                    return redirect('student-home') 

            else:
                return redirect('student-login')                       
        else:
            if request.path == 'admin-login':
                return redirect('admin-login')
            elif request.path == 'staff-login':
                 return redirect('staff-login')   
            elif request.path == 'student-login':
                return redirect('student-login')    
