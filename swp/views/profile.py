# -*- coding: utf-8 -*-
from django.shortcuts import render


def profile(request):
    return render(request, "swp/profile.html")
