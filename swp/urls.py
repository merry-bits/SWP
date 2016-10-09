# -*- coding: utf-8 -*-
from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth.views import login
from django.contrib.auth.views import logout

from .views import event
from .views import home
from .views import new_event
from .views import profile


_LOGIN_KWARGS = {
    "template_name": "swp/home.html",
    "redirect_authenticated_user": True,
}

urlpatterns = [
    url(r"^$", home, name="home"),
    url(r"^event/(?P<slug>[a-f0-9]{32})/$", event, name="event"),
    url(r"^event/(?P<slug>[a-f0-9]{32})/new$", new_event, name="new_event"),
    url(r"^profile/$", profile, name="profile"),
    url(r"^login$", login, name="login", kwargs=_LOGIN_KWARGS),
    url(r"^logout$", logout, name="logout", kwargs={"next_page": "home"}),
    url(r"^admin/", admin.site.urls),
]
