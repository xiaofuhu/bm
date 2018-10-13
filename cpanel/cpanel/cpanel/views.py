from django.shortcuts import render
import pyrebase
from django.contrib import auth

config = {

"apiKey": "AIzaSyCWhd3THR7JiuUctpYNLA_7kR24pMhfrp0",
    "authDomain": "bmdata-111111.firebaseapp.com",
    "databaseURL": "https://bmdata-111111.firebaseio.com",
    "projectId": "bmdata-111111",
    "storageBucket": "bmdata-111111.appspot.com",
    "messagingSenderId": "810944725832"
  }

firebase = pyrebase.initialize_app(config)

authe = firebase.auth()
database=firebase.database()
def signIn(request):
    return render(request, "signIn.html")

def postsign(request):
    email=request.POST.get('email')
    passw=request.POST.get('pass')
    try:
        user = authe.sign_in_with_email_and_password(email,passw)
    except:
        message="invalid credentials"
        return render(request,"signIn.html",{"messg":message})
    print(user['idToken'])
    session_id=user['idToken']
    request.session['uid']=str(session_id)
    return render(request, "welcome.html",{"e":email})
def logout(request):
    auth.logout(request)
    return render(request,'signIn.html')


def signUp(request):
    return render(request,"signup.html")

def postsignup(request):
    name=request.POST.get('name')
    email=request.POST.get('email')
    passw=request.POST.get('pass')
    role=request.POST.get('role')
    try:
        user=authe.create_user_with_email_and_password(email,passw)
    except:
        message="Unable to create account try again"
        return render(request,"signup.html",{"messg":message})

    uid = user['localId']
    data={"name":name,"role":role, "status":"1"}

    database.child("users").child(uid).child("details").set(data)
    return render(request,"signIn.html")

def create(request):
    
    return render(request,'create.html')


def post_create(request):
    
    import time
    from datetime import datetime, timezone
    import pytz
    
    tz= pytz.timezone('Asia/Kolkata')
    time_now= datetime.now(timezone.utc).astimezone(tz)
    millis = int(time.mktime(time_now.timetuple()))
    print("mili"+str(millis))
    work = request.POST.get('work')
    progress =request.POST.get('progress')
    url = request.POST.get('url')
    idtoken= request.session['uid']
    a = authe.get_account_info(idtoken)
    a = a['users']
    a = a[0]
    a = a['localId']
    print("info"+str(a))
    data = {
        "work":work,
        'progress':progress,
        'url':url
    }
    database.child('users').child(a).child('reports').child(millis).set(data)
    name = database.child('users').child(a).child('details').child('name').get().val()
    return render(request,'welcome.html', {'e':name})

def check(request):

    array_of_user_ids = database.child('users').shallow().get().val()
    work_id=[]
    work_name=[]
    for uid in array_of_user_ids or []:
        try:
            wor = database.child('users').child(uid).child('reports').shallow().get().val()
            work_id.extend(wor)
        except:
            pass
        for wid in wor or []:
            try:
                wor_n = database.child('users').child(uid).child('reports').child(wid).child('work').get().val()
                work_name.append(wor_n)
            except:
                pass

    comb_lis = work_name

    name = database.child('users').child(uid).child('details').child('name').get().val()
    return render(request, 'check.html', {'comb_lis': comb_lis, 'e': name})

def post_check(request):
    
    import datetime
    
    time = request.GET.get('z')
    
    idtoken = request.session['uid']
    a = authe.get_account_info(idtoken)
    a = a['users']
    a = a[0]
    a = a['localId']
    
    work =database.child('users').child(a).child('reports').child(time).child('work').get().val()
    progress =database.child('users').child(a).child('reports').child(time).child('progress').get().val()
    i = float(time)
    dat = datetime.datetime.fromtimestamp(i).strftime('%H:%M %d-%m-%Y')
    name = database.child('users').child(a).child('details').child('name').get().val()
    
    return render(request,'post_check.html',{'w':work,'p':progress,'d':dat,'e':name})
