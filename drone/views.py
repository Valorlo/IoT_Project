from array import array
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse,HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from drone.models import *
from django.utils import timezone
import hashlib
import json,string,random,socket,json,os,time,uuid
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
    return render(req,"login.html",{"name":name})

# decide the destination
def plan(req):
    # 不能目的地選到自己
    dest = mailOffices.objects.filter().exclude(name = req.session['name'])
    source = mailOffices.objects.filter(name = req.session["name"])[0]
    return render(req,"planDestination.html",{"api":GOOGLE_API,"dests":dest,"address_info":source.city+source.region+source.address})

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
        if mo[0].password == hash_code(psw) and 'name' not in req.session and len(mo)!=0:
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
        # destination's lat lng，要publish到broker
        lat = req.POST['lat']
        lat = req.POST['lng']
        mo = mailOffices.objects.filter(id = pid)[0]
        package = packages.objects.create(mailoffice = mo,counts = counts)
        return JsonResponse({'status':True})

# api/users/retrieve
@csrf_exempt
def api_retrieve(req):
    if req.method == 'POST':
        source_mid = req.POST['mid']
        mo = mailOffices.objects.filter(id = source_mid)[0]
        pInfo = packages.objects.filter(mailoffice = mo)[0]

        return JsonResponse({'status':True,
        'name':pInfo.mailoffice.name,
        'address':pInfo.mailoffice.city+pInfo.mailoffice.region+pInfo.mailoffice.address,
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

# api/drone/current
@csrf_exempt
def api_currentPos(req):
    # 網頁是用get method去抓無人機目前飛行的gps(subscribe)
    pass

# api/drone/rtl
@csrf_exempt
def api_rtl(req):
    if req.method == 'POST':
        # 這邊要publish"返航"的信號給無人機
        return JsonResponse({'status':True})