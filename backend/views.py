from django.shortcuts import render

def index(request):
    return render(request,'index.html')

def showfirebasejs(request):
    data = 'var firebaseConfig = {\
    apiKey: "AIzaSyBpleB2of_rb7_5A6He04wltfDQ4bZ4h24",\
    authDomain: "school-management-system-793c5.firebaseapp.com",\
    projectId: "school-management-system-793c5",\
    storageBucket: "school-management-system-793c5.appspot.com",\
    messagingSenderId: "160842190593",\
    appId: "1:160842190593:web:e4ad2d18144609f4b59500",\
    measurementId: "G-EJ740SLPR3"\
  };\
    firebase.initializeApp(firebaseConfig);\
    const messaging=firebase.messaging();\
    messaging.setBackgroundMessageHandler(function (payload) {\
        console.log(payload);\
        const notification=JSON.parse(payload);\
        const notificationOption={\
            body:notification.body,\
            icon:notification.icon\
        };\
        return self.registration.showNotification(payload.notification.title,notificationOption);\
    });'
    return HttpResponse(data)                       