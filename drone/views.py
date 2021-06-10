from django.shortcuts import render
from django.http import HttpResponse, JsonResponse,HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.template.loader import render_to_string
import hashlib
import json,string,random,socket,json,os,time,uuid
from datetime import datetime
import os

# Create your views here.

def frontPage(req):
    name = "Valorlo"
    return render(req,"frontPage.html",{"name":name})