from datetime import date, timedelta
import json
from django.http import JsonResponse
from django.shortcuts import render, redirect
import openai
from .forms import UserForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import QuestionAnswer
# Create your views here.

# open_api_key = "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"
# openai.api_key = open_api_key


@login_required(login_url="signin")
def index(request):
    today = date.today()
    yesterday = date.today() - timedelta(days=1)
    seven_days_ago = date.today() - timedelta(days=7)
    
    questions = QuestionAnswer.objects.filter(user=request.user)
    t_questions = questions.filter(created=today)
    y_questions = questions.filter(created=yesterday)
    s_questions = questions.filter(created__gte=seven_days_ago, created__lte=today)
    
    context = {"t_questions":t_questions, "y_questions": y_questions, "s_questions": s_questions}
    return render(request,"chatapp/index.html",context)

def signup(request):
    if request.user.is_authenticated:
        return redirect("index")
    form = UserForm()
    if request.method=='POST':
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            username = request.POST["username"]
            password = request.POST["password1"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request,user)
                return redirect("index")
    context = {"form": form}
    return render(request,"chatapp/signup.html",context)

def signin(request):
    err = None
    if request.user.is_authenticated:
        return redirect("index")
    if request.method=='POST':
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request,user)
            return redirect("index")
        else:
            err = "Invalid Credentials"
    context = {"err":err}
    return render(request,"chatapp/signin.html",context)

def signout(request):
    logout(request)
    return redirect("signin")

import requests

API_URL = "https://api-inference.huggingface.co/models/facebook/blenderbot-400M-distill"
headers = {"Authorization": "Bearer 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"}

def query(payload):
    data = json.dumps(payload)
    response = requests.request("POST", API_URL, headers=headers, data=data)
    return json.loads(response.content.decode("utf-8"))
    
	

# def ask_openai(messsage):
#     response = openai.ChatCompletion.create(
#     model="gpt-3.5-turbo",
#     messages=[
#             {"role": "system", "content": "You are a helpful assistant."},
#             {"role": "user", "content": messsage},
#         ]   
#     )
#     answer = response['choices'][0]['message']['content']
#     print(answer)

def getValue(request):
    data = json.loads(request.body)
    message = data["msg"]
    print(message)
    payload = {
        "inputs": message,
        "max_length": 200        
    }
    response = query(payload)
    answer = response.get("generated_text")
    QuestionAnswer.objects.create(user=request.user, question=message, answer = answer)
    return JsonResponse({"msg":message,"res":answer})