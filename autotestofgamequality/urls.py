"""autotestofgamequality URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from autotest.views import login, home, stresstest, result, report, error
from django.conf import settings
from django.conf.urls import handler404
from django.conf.urls.static import static
from django.views.static import serve

urlpatterns = [
    path('admin/', admin.site.urls),

    path("login/", login.login),
    path("logout", login.logout),
    path("", home.home),
    path("home/", home.home),

    path("stresstest/", stresstest.stress),
    path("stresstest/uninstall/", stresstest.uninstall),
    path("stresstest/fuzzy_uninstall", stresstest.fuzzy_uninstall),
    path("stresstest/install", stresstest.install),
    path("stresstest/execute/", stresstest.execute),
    path("stresstest/stop/", stresstest.stop),

    path("result/", result.result),

    path("report/", report.report),
    re_path(r'^result/media/(?P<path>.*)$', serve, {"document_root":settings.MEDIA_ROOT})
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

handler404 = error.page_not_found