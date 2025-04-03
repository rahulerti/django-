from django.shortcuts import render
import requests
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import HttpResponse
from django.http import JsonResponse
from django.template import loader
from .models import Po

#this is for sending html or plain text data
ht=HttpResponse
#JsonResponse is for sending json data
js=JsonResponse

# Create your views here.
def index(request):
    return ht("Hello, world. You're at the polls index.")

def index2(request):
    data={
        "name":"John",
        "age":30,
        "city":"New York"
    }    
    return js(data)

def web(request):
    tem=loader.get_template('index.html')
    return ht(tem.render())

@csrf_exempt
def save_use(request):
    if request.method == 'POST':
        data=json.loads(request.body)
        name = data.get('name')
        password = data.get('password')

        Po.objects.create(name=name, password=password)

        print(name, password)
        return js("Data saved successfully")
    
    else:
        return js({"message":"Invalid request method"})