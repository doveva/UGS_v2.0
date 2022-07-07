# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
from django.db import models
from django.contrib.auth.models import User


# Create your models here.
# Класс БД, содержащий название ПХГ
class UGSNames(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# Класс БД, содержащий точки отбора из ПХГ
class PointsOut(models.Model):
    name = models.ForeignKey(UGSNames, on_delete=models.CASCADE)
    X = models.FloatField()
    Y = models.FloatField()

    def __str__(self):
        return self.name


# Класс БД, содержащий точки закачки из ПХГ
class PointsIn(models.Model):
    name = models.ForeignKey(UGSNames, on_delete=models.CASCADE)
    X = models.FloatField()
    Y = models.FloatField()

    def __str__(self):
        return self.name


class UGSSettings(models.Model):
    name = models.ForeignKey(UGSNames, on_delete=models.CASCADE)
    capacity = models.BigIntegerField()
    volume_in = models.FloatField()
    volume_out = models.FloatField()

    def __str__(self):
        return self.name


class Repairs(models.Model):
    name = models.ForeignKey(UGSNames, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    in_coeff = models.FloatField()
    out_coeff = models.FloatField()

    def __str__(self):
        return self.name

