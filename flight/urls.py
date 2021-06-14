"""flight URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.urls import path,include,re_path
from django.conf.urls import url
from django.conf.urls.static import static
from django.conf import settings
import drone.views as dviews

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', dviews.frontPage),
    path('plan',dviews.plan),
    path('logout',dviews.logout),

    # api url
    re_path(r'api/users/regist',dviews.api_regist),
    re_path(r'api/users/login',dviews.api_login),
    re_path(r'api/users/confirm',dviews.api_confirm),
]
