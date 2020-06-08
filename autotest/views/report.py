import os

from django.shortcuts import render
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from autotest.app_settings import AppSettings



@login_required(login_url="login")
def report(request):
    username = request.session.get("user")
    if request.GET.get:
        game = AppSettings.GAMES[request.GET.get("game")]
        report = request.GET.get("report")
        html = "testers/{}/{}/log/{}.html".format(username, game, report)
        return render(request, html)