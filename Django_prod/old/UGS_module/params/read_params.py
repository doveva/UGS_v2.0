#!/usr/bin/env python
import json
import sys
import os

try:
    with open(r'Python_modules/UGS_module/json_data/params_model.json', 'r', encoding="utf-8") as f:
        params_data = json.load(f)
except FileNotFoundError:
    sys.exit("Ошибка: Файл c параметрами не найден!:" + os.getcwd())

params = ['intra_month', 'weights_in', 'weights_out', 'functions', 'flows', 'gmt', 'date']

variable = []
for key, value in params_data.items():
    if key == 'intra_month':
        intra_month = value
        variable.append(key)
    elif key == 'weights_in':
        weights_in = value
        variable.append(key)
    elif key == 'weights_out':
        weights_out = value
        variable.append(key)
    elif key == 'params_phg':
        params_phg = value
        variable.append(key)
    elif key == 'functions':
        functions = value
        variable.append(key)
    elif key == 'flows':
        flows = value
        variable.append(key)
    elif key == 'gmt':
        gmt = value
        variable.append(key)
    elif key == 'country_phg':
        country_phg = value
    elif key == 'date':
        date = value
        variable.append(key)
    else:
        print(f'Неопределенный параметр {key}')

check = set(params).difference(set(variable))

if not check:
    del check, params_data, variable, params, key, value, f
else:
    sys.exit(f"Не хватает данных по {check}")

class Params(object):
    """ Класс параметров!
    """

    def __init__(self):
        self.intra_month = intra_month
        self.weights_in = weights_in
        self.weights_out = weights_out
        self.params_phg = params_phg
        self.functions = functions
        self.flows = flows
        self.gmt = gmt
        self.country_phg = country_phg
        self.date = date

    def __str__(self):
        return f"ПХГ:{list(self.params_phg.keys())}"

