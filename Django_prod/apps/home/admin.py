# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib import admin
from apps.api.models import PointsIn, UGSNames, PointsOut, Repairs
# Register your models here.

admin.site.register(PointsIn)
admin.site.register(UGSNames)
admin.site.register(PointsOut)
admin.site.register(Repairs)