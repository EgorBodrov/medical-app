from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from med.models import *
from .chatSockets import socketServer
import json
import random
import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

server = socketServer()
port = 465  # For SSL
smtp_server = "smtp.gmail.com"
sender_email = "medapp322@gmail.com"
password = "Qwerty2312"


@login_required
@csrf_exempt
def createChat(request):
    if request.method == "POST":
        chat = Chat()
        chat.save()
        user1 = request.user
        user2 = User.objects.get(id=request.POST['receiver'])
        chat.users.add(user1, user2)
        chat.save()
        return HttpResponse(status=201)
    else:
        return HttpResponseForbidden("Forbidden")


@login_required
@csrf_exempt
def sendMessage(request):
    if request.method == "POST":
        mes = Message()
        mes.chat = Chat.objects.get(id=request.POST['chatId'])
        mes.text = request.POST['text']
        mes.sender = request.POST['sender']
        mes.save()
        target = mes.chat.users.exclude(id=mes.sender).first()
        server.send_message(target.id, mes.text)
        return HttpResponse(status=201)
    else:
        return HttpResponseForbidden("Forbidden")


@csrf_exempt
def sendVerificationCode(request):
    if request.method == "POST" and request.content_type == 'application/json':
        data = json.loads(request.body)
        email = data['email']
        code = "".join(random.sample([str(i) for i in range(10)], 6))
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender_email, password)
            msg = MIMEMultipart("alternative")
            msg["Subject"] = u'MedApp Verification code'
            msg["From"] = u"MedApp"
            part1 = MIMEText(u'Your verification code: {}'.format(code),
                             "plain", "utf-8")
            msg.attach(part1)
            server.sendmail(sender_email, email, msg.as_string())
        return HttpResponse(json.dumps({'code': code}), content_type="application/json")

        # mes = Message()
        # mes.chat = Chat.objects.get(id=request.POST['chatId'])
        # mes.text = request.POST['text']
        # mes.sender = request.POST['sender']
        # mes.save()
        # target = mes.chat.users.exclude(id=mes.sender).first()
        # server.send_message(target.id, mes.text)
        # return HttpResponse(status=201)
    else:
        return HttpResponseForbidden("Forbidden")


@csrf_exempt
def registerUser(request):
    if request.method == "POST":
        user = User()
        user.first_name = request.POST['name']
        user.last_name = request.POST['surname']
        user.email = request.POST['email']
        user.username = request.POST['email']
        user.set_password(request.POST['password'])
        user.save()
        patient = Patient(phone=request.POST['phone'], user=user)
        patient.save()
        login(request, user)
        return HttpResponse(status=201)
    else:
        return HttpResponseForbidden("Forbidden")
