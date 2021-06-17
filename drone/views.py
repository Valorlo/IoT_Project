from array import array
from django.core import mail
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse,HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from drone.models import *
from django.utils import timezone
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from email.utils import make_msgid 
import hashlib
import json,string,random,socket,os,time,uuid
from datetime import date, datetime
import hashlib #用於加密密碼
from .key import secret
import os

# Create your views here.

GOOGLE_API = secret().api

def hash_code(s, salt='valorlo'):  # 密碼加密
    h = hashlib.sha256()
    s = s + salt
    h.update(s.encode())
    return h.hexdigest()

# -----------------------web request-----------------------

# authenticate, load first page
def frontPage(req):
    name = req.session.get('name',False)
    if name:
        return HttpResponseRedirect("/plan")
    else:
        return render(req,"login.html")

# decide the destination
def plan(req):
    # 不能目的地選到自己
    dest = mailOffices.objects.filter().exclude(name = req.session['name'])
    source = mailOffices.objects.filter(name = req.session["name"])[0]
    return render(req,"planDestination.html",{"api":GOOGLE_API,
    "dests":dest,
    "address_info":source.city+source.region+source.address,
    "name":req.session['name']
    })

# logout
def logout(req):
    req.session.flush()
    return JsonResponse({'result': True})

# -----------------------api request-----------------------

# api/users/regist
@csrf_exempt
def api_regist(req):
    if req.method == 'POST':
        name = req.POST['mName']
        email = req.POST['mEmail']
        pw = req.POST['mPw']
        city = req.POST['mCity']
        region = req.POST['mRegion']
        address = req.POST['mAddress']
        mo = mailOffices.objects.create(name = name,password = hash_code(pw), email = email, city=city, region = region, address = address)
        return JsonResponse({'status':True})

# api/users/login
@csrf_exempt
def api_login(req):
    if req.method == 'POST':
        account = req.POST['account']
        psw = req.POST['psw']
        mo = mailOffices.objects.filter(email = account)
        if len(mo)!=0:
            if mo[0].password == hash_code(psw) and 'name' not in req.session:
                req.session['name'] = mo[0].name
                return JsonResponse({'status':True})
        else:
            return JsonResponse({'status':False})

# api/users/confirm
@csrf_exempt
def api_confirm(req):
    if req.method == 'POST':
        pid = req.POST['pid']
        counts = int(req.POST['counts'])
        # 跟無人機講 GO 跟 destination's lat lng，要publish到broker
        lat = req.POST['lat']
        lat = req.POST['lng']
        dest = mailOffices.objects.filter(id = pid)[0]
        source = mailOffices.objects.filter(name = req.session['name'])[0]
        package = packages.objects.create(dest_office = dest,source_office = source,counts = counts)
        return JsonResponse({'status':True})

# api/users/retrieve
@csrf_exempt
def api_retrieve(req):
    if req.method == 'POST':
        dest_mid = req.POST['mid']
        dest = mailOffices.objects.filter(id = dest_mid)[0]
        pInfo = packages.objects.filter(dest_office = dest)[0]

        return JsonResponse({'status':True,
        'name':pInfo.source_office.name,
        'address':pInfo.source_office.city+pInfo.source_office.region+pInfo.source_office.address,
        "time":pInfo.deliver,
        'counts':pInfo.counts,
        'pid':pInfo.id})

# api/users/signfor
@csrf_exempt
def api_signfor(req):
    if req.method == 'POST':
        pid = req.POST['pid']
        pInfo = packages.objects.filter(id = pid)
        arrived = timezone.now()
        pInfo.update(taken = True)
        pInfo.update(arrived = arrived)

        return JsonResponse({'status':True,"arrive_time":arrived})

# api/users/sendEmail
@csrf_exempt
def api_sendEmail(req):
    if req.method == "POST":
        pid = req.POST["pid"]
        package_info = packages.objects.filter(id = pid)[0]
        email_template = render_to_string(
            '../templates/email_template.html',
            {
                'pid': pid,
                "office_name":package_info.dest_office.name
            }
        )
        email = EmailMessage(
            '包裹抵達囉！',  # 電子郵件標題
            email_template,  # 電子郵件內容
            settings.EMAIL_HOST_USER,  # 寄件者
            [package_info.dest_office.email, package_info.source_office.email]  # 收件者
        )
        email.content_subtype = "html"
        email.fail_silently = False
        email.send()
        return JsonResponse({'status':True})

# api/drone/current
@csrf_exempt
def api_currentPos(req):
    # 網頁是用get method去抓無人機目前飛行的gps(subscribe)，如果sub到-1的值的話就代表無人機到了
    pass

# api/drone/rtl
@csrf_exempt
def api_rtl(req):
    if req.method == 'POST':
        # 這邊要publish"返航"的信號給無人機
        return JsonResponse({'status':True})