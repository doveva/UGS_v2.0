#!/usr/bin/env python
# -*- coding: utf-8 -*-

from calendar import monthrange
import sys

def test_weights(weights: dict):
    """ Проверка равенства суммы весов для направлений 1
    """

    for key, value in weights.items():
        if abs(1 - sum(value.values())) > 1e-5 :
            print(f'Сумма весов для {key} не равна 1 {value.values()} {sum(value.values())}')
            return -1

    return 0


def test_intra_month(intra_month: dict):
    """ Проверка длинны массивов для внутримсячных значений
    """

    for phg, data in intra_month.items():
        for year, data1 in data.items():
            for month, data2 in data1.items():
                n = len(data2)
                if monthrange(int(year), int(month))[1] != n:
                    print(f'ПХГ {phg} для года {year}, месяца {month}' \
                          + f', число значений не верно = {n}!')
                    return -1

    return 0


def searh_position(lst, value):
    """ Посик номера позиции элемента value в списке lst
    """

    arr = []
    i = 0
    for elem in lst:
        if elem == value:
            arr.append(i)
        i += 1

    return arr


def test_flows(flows: dict):
    """ Проверка длины массивов и их значений на корректность.
    """

    check_value = lambda y: len(list(filter(lambda x: (x != 0) & (x != 1), y)))


    def test_value(arr, name):

        if check_value(arr[name]) > 0:
            print(f'Для {phg}, {year}, flow = {name} значения не равны 0/1')
            return True
        return False

    def test_len(arr, name):

        if len(arr[name]) != 12:
            print(f'Для {phg}, {year}, flow = {name} длина массива должна быть 12')
            return True
        return False

    f1 = 'in'; f2 = 'out'
    for phg, data in flows.items():
        for year, data1 in data.items():

            if test_len(data1, f1):
                return -1
            if test_len(data1, f2):
                return -1
            if test_value(data1, f1):
                return -1
            if test_value(data1, f2):
                return -1

    return 0


def test_functions(functions: dict):
    """ Проверка корректности точек кривых доходности.
    """

    check_value = lambda y: len(list(filter(lambda x: (x > 1) or (x < 0), y)))

    def test_value(z):
        if check_value(z) > 0:
            print(f'Для ПХГ {phg} потока {flow} координата не корретная (больше 1 / меньше 0)')
            return True
        return False

    for phg, flows in functions.items():
        for flow, coord in flows.items():
            if test_value(coord['x']):
                return -1
            if test_value(coord['y']):
                return -1

    return 0


def test_gmt(gmt: dict):
    """Проверка корректности данных по ГМТ:
    длтнна масиваи и отсутсвие отрицательных значений!
    """

    test_len = lambda y: len(list(filter(lambda x: x < 0, y)))
    for phg, values in gmt.items():
        for year, value in values.items():
            x_in = value['in']
            x_out = value['out']
            if len(x_in) != 12 or len(x_out) != 12:
                print(f'Для ПХГ (по ГМТ) {phg} года {year} длинна массива не равна 12')
                return -1
            if test_len(x_in) > 0 or test_len(x_out) > 0:
                print(f'Для ПХГ (по ГМТ) {phg} года {year} значения отрицательные!')
                return -1

    return 0


def test_params(params_phg: dict):
    """ Проверка наличия начальных параметров ПХГ.
    """

    arr = ['volume_in', 'volume_out', 'capacity', 'balance_gpe', 'balance_gmt']
    for phg, param in params_phg.items():
        test_arr = set(arr).difference(set(param.keys()))
        if len(test_arr) != 0:
            print(f'ПХГ {phg} не хватает параметров {test_arr}')
            return -1

    return 0


def test_intra_month_vs_flows(intra_month, flows):
    """ Проверка соответсвий распределения в потоках:
    месяцы для одновренменной закачки/отбора и наличия сумм по этим месяцам
    """

    for phg, values in intra_month.items():
        for year in values:
            im = map(lambda x: int(x), intra_month[phg][year].keys())
            flow = []
            value = flows[phg][year]
            for i in range(12):
                if value['in'][i] + value['out'][i] == 2:
                    flow.append(i + 1)
            diff = set(flow).symmetric_difference(set(im))
            if diff:
                print(f"Для {phg} года {year} есть несоответствия в потоках месяцев {diff}")
                return -1

    return 0
