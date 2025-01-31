# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('evaluate/', views.evaluate, name='evaluate'),
    path('history/', views.history, name='history'),
    path('task_status/<str:task_id>/', views.task_status, name='task_status'),
]
