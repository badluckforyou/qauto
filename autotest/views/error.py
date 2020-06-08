from django.shortcuts import render

from autotest.app_settings import AppSettings

def page_not_found(request, exception):
    '''404页面'''
    return render(request, 'templates/404.html', {'title': AppSettings.TITLE})