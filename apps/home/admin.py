# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib import admin
from .models import Points_in, UGS_names, Points_out
# Register your models here.

admin.site.register(Points_in)
admin.site.register(UGS_names)
admin.site.register(Points_out)