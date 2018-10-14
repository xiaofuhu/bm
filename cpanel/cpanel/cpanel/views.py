from django.shortcuts import render
import pyrebase
from django.contrib import auth
from django.urls import reverse

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
    tz= pytz.timezone('US/Michigan')
    time_now= datetime.now(timezone.utc).astimezone(tz)
    millis = int(time.mktime(time_now.timetuple()))
    print("mili"+str(millis))
    work = request.POST.get('work')
    location =request.POST.get('location')
    wage =request.POST.get('wage')
    skill_req =request.POST.get('skill_req')
    url = request.POST.get('url')
    idtoken= request.session['uid']
    a = authe.get_account_info(idtoken)
    a = a['users']
    a = a[0]
    a = a['localId']
    print("info"+str(a))
    data = {
        'work':work,
        'location':location,
        'wage':wage,
        'skill_req':skill_req,
    }
    database.child('users').child(a).child('reports').child(millis).set(data)
    name = database.child('users').child(a).child('details').child('name').get().val()
    return render(request,'welcome.html', {'e':name})

def check(request):

    array_of_user_ids = database.child('users').shallow().get().val()
    work_id=[]
    work_name=[]
    work_location=[]
    work_wage=[]
    work_skill_req=[]
    for uid in array_of_user_ids or []:
        try:
            wor = database.child('users').child(uid).child('reports').shallow().get().val()
            work_id.extend(wor)
        except:
            pass
        for wid in wor or []:
            try:
                wor_n = database.child('users').child(uid).child('reports').child(wid).child('work').get().val()
                wor_l = database.child('users').child(uid).child('reports').child(wid).child('location').get().val()
                wor_w = database.child('users').child(uid).child('reports').child(wid).child('wage').get().val()
                wor_s = database.child('users').child(uid).child('reports').child(wid).child('skill_req').get().val()
                work_name.append(wor_n)
                work_location.append(wor_l)
                work_wage.append(wor_w)
                work_skill_req.append(wor_s)
            except:
                pass

    comb_lis = {work_name,work_location,work_wage,work_skill_req}

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
    location =database.child('users').child(a).child('reports').child(time).child('location').get().val()
    wage =database.child('users').child(a).child('reports').child(time).child('wage').get().val()
    skill_req =database.child('users').child(a).child('reports').child(time).child('skill_req').get().val()
    i = float(time)
    dat = datetime.datetime.fromtimestamp(i).strftime('%H:%M %d-%m-%Y')
    name = database.child('users').child(a).child('details').child('name').get().val()
    
    return render(request,'post_check.html',{'w':work,'l':location,'w':wage,'s':skill_req,'d':dat,'e':name})
