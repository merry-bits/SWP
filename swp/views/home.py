# -*- coding: utf-8 -*-
from django.shortcuts import render

from swp.models import Event


def home(request):
    events = Event.objects.filter(visible=True).order_by("-event_date")
    return render(request, "swp/home.html", {"events": events})
