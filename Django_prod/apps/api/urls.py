# -*- encoding: utf-8 -*-
"""
"""

from django.urls import path
from . import views


urlpatterns = [
    path('UGS_charts/', views.ugs_charts),
    path('Repairs/', views.repairs_create_api_view)
]
