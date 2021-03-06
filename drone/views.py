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
from geopy.distance import geodesic
import hashlib
import json,string,random,socket,os,time,uuid
from datetime import date, datetime
import hashlib #用於加密密碼
from .key import secret
import os
import time
from paho.mqtt import client as mqtt_client

GOOGLE_API = secret().api
broker = '140.127.208.60'
port = 1883
GPS_topic = "AILAB/IOT/DRONE/GPS"
STAT_topic = "AILAB/IOT/DRONE/STAT"
HIGH_topic = "AILAB/IOT/DRONE/HIGH"
pub_DST = "AILAB/IOT/SERVER/DST"
pub_GO = "AILAB/IOT/SERVER/GO"
pub_RTL = "AILAB/IOT/SERVER/RTL"
client_id = f'python-mqtt-{random.randint(0, 100)}'
GPS_reply = ""
STAT_reply = ""
dst_loc = ""
dst_lat = ""
dst_lng = ""

# def drone_init(client: mqtt_client):
#     msg = ""
#     result = client.publish(pub_DST, json.dumps(msg))
#     msg = "0"
#     result = client.publish(pub_RTL, json.dumps(msg))
#     msg = "0"
#     result = client.publish(pub_GO, json.dumps(msg))

# -----------------------mqtt functions-----------------------

def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    # client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def GPS_subscribe(client: mqtt_client):
    # print("subscribe")
    def on_message(client, userdata, msg):
        global GPS_reply
        # print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        GPS_reply = msg.payload.decode()
        # GPS_reply = switch_control['value'][0]
        print(GPS_reply)

    client.subscribe(GPS_topic)
    client.on_message = on_message

def STAT_subscribe(client: mqtt_client):
    # print("subscribe")
    def on_message(client, userdata, msg):
        global STAT_reply
        # print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        STAT_reply = msg.payload.decode()
        # GPS_reply = switch_control['value'][0]
        print(STAT_reply)

    # print("out",GPS_reply)
    client.subscribe(STAT_topic)
    client.on_message = on_message

def publish_DST(client,where):
    msg = where
    result = client.publish(pub_DST, json.dumps(msg))
    # result: [0, 1]
    status = result[0]
    if status == 0:
        print(f"Send `{msg}` to topic `{pub_DST}`")
    else:
        print(f"Failed to send message to topic {pub_DST}")

    # time.sleep(30)

def publish_RTL(client):
    msg =True
    result = client.publish(pub_RTL, json.dumps(msg))
    # result: [0, 1]
    status = result[0]
    if status == 0:
        print(f"Send `{msg}` to topic `{pub_RTL}`")
    else:
        print(f"Failed to send message to topic {pub_RTL}")

def publish_GO(client):
    msg =True
    result = client.publish(pub_GO, json.dumps(msg))
    # result: [0, 1]
    status = result[0]
    if status == 0:
        print(f"Send `{msg}` to topic `{pub_GO}`")
    else:
        print(f"Failed to send message to topic {pub_GO}")

# -----------------------web request-----------------------

# hash password
def hash_code(s, salt='valorlo'):  # 密碼加密
    h = hashlib.sha256()
    s = s + salt
    h.update(s.encode())
    return h.hexdigest()

# authenticate, load first page
def frontPage(req):
    name = req.session.get('name',False)
    if name:
        return HttpResponseRedirect("/plan")
    else:
        return render(req,"login.html")

# decide the destination
def plan(req):
    name = req.session.get('name',False)
    if name:
    # 不能目的地選到自己
        dest = mailOffices.objects.filter().exclude(name = req.session['name'])
        source = mailOffices.objects.filter(name = req.session["name"])[0]
        return render(req,"planDestination.html",{"api":GOOGLE_API,
        "dests":dest,
        "address_info":source.city+source.region+source.address,
        "name":req.session['name']
        })
    else:
        return HttpResponseRedirect("/")

# logout
def logout(req):
    req.session.flush()
    return JsonResponse({'result': True})

# record
def record(req):
    name = req.session.get('name',False)
    if name:
    # 不能目的地選到自己
        record = packages.objects.filter()
        return render(req,"record.html",{"pList":record,"name":req.session['name']})
    else:
        return HttpResponseRedirect("/")

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
    global dst_lat,dst_lng
    if req.method == 'POST':
        client = connect_mqtt()
        pid = req.POST['pid']
        counts = int(req.POST['counts'])
        # publish_GO(client)
        # 跟無人機講 GO 跟 destination's lat lng，要publish到broker
        lat = req.POST['lat']
        lng = req.POST['lng']
        dst_lat = float(lat)
        dst_lng = float(lng)
        dst_loc = lat+"@"+lng
        print(dst_loc)
        
        # start_time = time.time()
        # while True:
        publish_DST(client,lat+"@"+lng)
            
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
temp = ""
# api/drone/current
@csrf_exempt
def api_currentPos(req):
    global temp
    # subscribe無人機目前飛行的gps
    arrive = False
    client = connect_mqtt()
    while True:
        GPS_subscribe(client)
        # print("GPS_reply",GPS_reply)
        # print("temp",temp)
        
        if GPS_reply != "":
            split_GPS = GPS_reply.split('@')
            if geodesic((float(split_GPS[0]),float(split_GPS[1])),(dst_lat, dst_lng)) <= 0.01:
                arrive = True
                break
        if GPS_reply != "" and GPS_reply != temp:
            temp = GPS_reply


            
            break
        client.loop()
    print("get new GPS")
    if GPS_reply != "":
        split_GPS = GPS_reply.split('@')
        cp = []
        cp.append(float(split_GPS[0]))
        cp.append(float(split_GPS[1]))
        return JsonResponse({"status":True,"currentP":cp,"arrive":arrive})
    else:
        return JsonResponse({"status":False})

# api/drone/state
@csrf_exempt
def api_droneState(req):
    # subscribe無人機目前的狀態
    client = connect_mqtt()
    while True:
        STAT_subscribe(client)
        if STAT_reply != "":
            break
        client.loop()
    
    if STAT_reply != "":
        return JsonResponse({"state":STAT_reply})
    else:
        return JsonResponse({"state":False})

# api/drone/rtl
@csrf_exempt
def api_rtl(req):
    if req.method == 'POST':
        # 這邊要publish"返航"的信號給無人機
        client = connect_mqtt()
        publish_RTL(client)
        return JsonResponse({'status':True})