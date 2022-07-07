#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 11 18:17:26 2022

@author: Alexander
"""


from calendar import monthrange
from copy import deepcopy
import numpy as np
import pandas as pd
from Python_modules.UGS_module.functions.exceptions import UserException


def get_linear_coeff(x, y):
    """ Создание коэффициентов линейной функции по точкам.
    """

    if len(x) - len(y) != 0:
        raise ValueError("\nРазная длина массивов")

    k, b = [], []
    for i in range(len(x) - 1):
        if x[i + 1] - x[i] == 0:
            continue
        coeff = (y[i + 1] - y[i])/(x[i + 1] - x[i])
        k.append(coeff)
        b.append(y[i] - coeff * x[i])

    return k, b


def get_optimum(days, flow, balance, volume_in, volume_out, capacity):
    """ Определение коэффициентоы прямой оптимальности для ПХГ
    """

    n = days - 1

    if n <= 0:
        raise ValueError("Info: Число дней меньше 2")

    if flow == 'in':
        volume = -volume_in
    elif flow == 'out':
        volume = volume_out
    else:
        raise NameError("\nОшибка: Переменна flow должна быть in/out")

    k = capacity / (-volume * n)
    b = balance / (volume * n)

    return k, b


def get_break_point(x):
    """ Определение точек разрыва через повторяющиеся значения
        по точкам оси OX.
        x - список точек оси ОХ.
    """

    points = []
    for i in range(len(x) - 1):
        if x[i] == x[i + 1]:
            points.append(x[i])

    return points


def get_interpolate(x0, x, y):
    """ Линейная интерполяция
    """

    if len(x) - len(y) != 0:
        raise ValueError("Разная длина массива для интерполяции")

    # Сортировка массивров про возрастанию относительно массива x
    x, y = list(zip(*sorted(list(zip(x, y)), key=lambda x: x[0])))

    if x0 >= max(x):
        return y[-1]
    if x0 < min(x):
        return y[0]

    for i in range(len(x) - 1):
        if x[i] <= x0 < x[i + 1]:
            k = (y[i + 1] - y[i])/(x[i + 1] - x[i])
            b = y[i] - k * x[i]
            return x0 * k + b


def get_step_value(x, y, days, flow, decrease=1, correct=1, **params):
    """ Определение оптимального шага изменеия при закачке и обора газа.
    decrease - снижение коэффициента (алгоритмическое)
    correct  - cнижение коэффициета (технический работы)
    """

    if not (0 < decrease <= 1): decrease = 1

    x = np.array(x)
    y = np.array(y)

    k_coeff, b_coeff = get_linear_coeff(x, y)
    break_points = get_break_point(x)

    try:
        k0, b0 = get_optimum(days, flow, **params)
    except ValueError as msg:
        print(msg)
        x0_ = params['balance'] / params['capacity']
        y0_ = get_interpolate(x0_, x, y)
        return x0_, y0_ * decrease * correct

    x0_ = -b0 / k0
    y0_ = get_interpolate(x0_, x, y)

    if (x0_ >= 1 and flow == 'in') or (x0_ <= 0 and flow == 'out'):
        return x0_, 0

    intersection = False
    x = np.unique(x)
    for i in range(len(x) - 1):
        x0 = (b_coeff[i] - b0)/(k0 - k_coeff[i])
        if x[i] <= x0 < x[i + 1]:
            y0 = x0 * k_coeff[i] + b_coeff[i]
            intersection = True
            break

    z0 = 1
    for point in break_points:
        z0_ = k0 * point + b0
        if z0 < z0_ and z0_ > 0:
            z0 = z0_

    if not intersection and z0 < 1:
        y0 = min(y0_, z0)
    elif intersection:
        y0 = min(y0_, y0, z0)
    else:
        y0 = 0

    x0 = (y0 - b0) / k0

    return x0, y0 * decrease * correct


def create_dynamics(phg: str, functions: dict, tech_availability: dict, decrease: float):
    """ Создание объекта динамики для ПХГ и функции производительности.
    """

    def get_arrays(flow, days, params:dict, gmt=0):
        """ Создание динаимкм по дням для ПХГ в зависимости от потоков и параметров ПХГ.
        """

        par = params[phg]
        func = functions[phg]
        tech = tech_availability[phg]

        if gmt:
            decrease_ = decrease
        else:
            decrease_ = 1

        if flow == 'in':
            par['balance'] = par['balance'] + gmt * days
            x, y = get_step_value(*func[flow].values(), days=days, flow=flow, decrease=decrease_,
                                    correct=tech[flow], **par)
            step = y * par['volume_in']
            fact_in = np.array([step] * days) * tech[flow]
            fact_out = np.array([0] * days)
        elif flow == 'out':
            par['balance'] = par['balance'] - gmt * days
            x, y = get_step_value(*func[flow].values(), days=days, flow=flow, decrease=decrease_,
                                    correct=tech[flow], **par)
            step = (-1) * y * par['volume_out']
            fact_out = np.array([-step] * days) * tech[flow]
            fact_in = np.array([0] * days)
        else:
            step = 0
            fact_out = np.array([0] * days)
            fact_in = np.array([0] * days)

        balance = np.append(par['balance'], par['balance'] + np.array([step] * (days - 1)).cumsum())
        ratios = balance / par['capacity']
        balance += step

        if (ratios > 1 + 0.01).any():
            raise UserException(f"\nЗнаечние Баланса превышает мощность ПХГ: {phg}!")
        if (ratios < 0 - 0.01).any():
            raise UserException(f"\nЗначение Баланса отрицательно для ПХГ: {phg}!")

        tech_in = np.array(list(map(
            lambda x0: get_interpolate(x0, **func['in']), ratios))) * par['volume_in'] * tech['in']
        tech_out = np.array(list(map(
            lambda x0: get_interpolate(x0, **func['out']), ratios))) * par['volume_out'] * tech['out']
        del ratios

        if (fact_in > tech_in + 1).any():
            raise UserException("\nФактическое знаение Закачки выше техничесгкой возможности!")
        if (fact_out > tech_out + 1).any():
            raise UserException("\nФактическое знаение Отбора выше техничесгкой возможности!")

        # Корректировка баланса
        if flow == 'in':
            balance = balance - gmt * days + np.array([gmt] * days).cumsum()
        elif flow == 'out':
            balance = balance + gmt * days - np.array([gmt] * days).cumsum()

        return tech_in, fact_in, tech_out, fact_out, balance

    return get_arrays


def get_dynamics(phg: str, functions: dict, flows: dict, params: dict,
                intra_month: dict, gmt: dict, tech_availability: dict, init_date:str, decrease):
    """ Создание динимики по годам в зависимоти от ПХг и структуры закачки/отбора.
    v0
    """

    params_ = deepcopy(params)

    arr_balance = np.array([])
    arr_tech_in, arr_tech_out = np.array([]), np.array([])
    arr_fact_in, arr_fact_out = np.array([]), np.array([])

    get_arrays_ = create_dynamics(phg, functions, tech_availability, decrease)

    data_flow = flows[phg]
    data_gmt = gmt[phg]

    months = np.array([])
    years = np.array([])

    init_date = pd.to_datetime(init_date, format='%d-%m-%Y')
    init_month = init_date.month - 1

    def get_distr_intra_month(value, day):
        """ Распределение флэта внутремесячно!
        value > 0 и value != 1 - закачка
        value < 0 b value != -1 - отбор
        value = 0 - без закачки и отбора
        """

        zero = np.array([0] * day)
        value_ = np.array([abs(value)] * day)

        if value >= 0 and value != 1:
            fact_in = value_
            fact_out = zero
        elif value < 0 and value != -1:
            fact_in = zero
            fact_out = value_

        balance = params_[phg]['balance'] + np.sign(value) * value_.cumsum()
        ratios = balance / params_[phg]['capacity']

        if (ratios > 1 + 0.01).any() or (ratios < 0 - 0.01).any():
            raise UserException(f"\nПредупреждение:\nНедопустиное значение {value} для" + \
                f" внутримесячной Закачки/Отбора ПХГ: {phg}, {year} года, {month + 1}-го месяца!")

        tech_in = np.array(list(map(
            lambda x0: get_interpolate(x0, **functions[phg]['in']), ratios))) * \
                params_[phg]['volume_in']
        tech_out = np.array(list(map(
            lambda x0: get_interpolate(x0, **functions[phg]['out']), ratios))) * \
                params_[phg]['volume_out']

        return tech_in, fact_in, tech_out, fact_out, balance

    for year in data_flow:
        inj, wid = data_flow[year]['in'], data_flow[year]['out']
        for month in range(init_month, 12):
            try:
                days = monthrange(int(year), month + 1)[1]
                # Закачка
                if inj[month] == 1 and wid[month] == 0:
                    gmt_in = data_gmt[year]['in']
                    tech_in, fact_in, tech_out, fact_out, balance = \
                        get_arrays_('in', days, params_, gmt_in[month])
                # Отбор
                elif inj[month] == 0 and wid[month] == 1:
                    gmt_out = data_gmt[year]['out']
                    tech_in, fact_in, tech_out, fact_out, balance = \
                        get_arrays_('out', days, params_, gmt_out[month])
                # Отбор и закачка отсутсвуют
                elif inj[month] == 0 and wid[month] == 0:
                     tech_in, fact_in, tech_out, fact_out, balance = \
                         get_arrays_('empty', days, params_)
                # Закачка и Отбор
                elif inj[month] == 1 and wid[month] == 1:
                    gmt_out = data_gmt[year]['out']
                    gmt_in = data_gmt[year]['in']

                    tech_in, fact_in = np.array([]), np.array([])
                    tech_out, fact_out = np.array([]), np.array([])
                    balance = np.array([])

                    distr = get_count_element(intra_month[phg][year][str(month + 1)])
                    for i, day in distr:
                        if i == 1:
                            tech_in_, fact_in_, tech_out_, fact_out_, balance_ = \
                                get_arrays_('in', day, params_, gmt_in[month] )
                        elif i == -1:
                            tech_in_, fact_in_, tech_out_, fact_out_, balance_ = \
                                get_arrays_('out', day, params_, gmt_out[month])
                        else:
                            try:
                                tech_in_, fact_in_, tech_out_, fact_out_, balance_ = get_distr_intra_month(i, day)
                            except UserException as msg:
                                print(msg.args[0] + ": Результат - внутримесячная закачка/отбор снижена до нуля!")
                                tech_in_, fact_in_, tech_out_, fact_out_, balance_ = get_distr_intra_month(0, day)

                        tech_in = np.append(tech_in, tech_in_);fact_in = np.append(fact_in, fact_in_)
                        tech_out = np.append(tech_out, tech_out_);fact_out = np.append(fact_out, fact_out_)
                        balance = np.append(balance, balance_)

                        params_[phg]['balance'] = balance_[-1]

                else:
                    continue

            except UserException as msg:
                raise UserException(("" + msg.args[0] + " для года {0}, месяца {1}" + \
                    " - требуектся снизить коэффициент").format(year, month + 1))

            if not (inj[month] == 1 and wid[month] == 1):
                params_[phg]['balance'] = balance[-1]

            months_label = dict(zip(range(init_month, 12), ['Январь', 'Февраль', 'Март', 'Апрель',
                'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'][init_month:]))

            months = np.append(months, [months_label[month]] * days)
            years = np.append(years, [year] * days)

            arr_tech_in = np.append(arr_tech_in, tech_in)
            arr_fact_in = np.append(arr_fact_in, fact_in)
            arr_tech_out = np.append(arr_tech_out, tech_out)
            arr_fact_out = np.append(arr_fact_out, fact_out)
            arr_balance = np.append(arr_balance, balance)

        # Для последующих лет начало месяца - январь (0)
        init_month = 0

    return years, months, arr_tech_in, arr_fact_in, arr_tech_out, arr_fact_out, arr_balance


def get_count_element(arr):
    """ Количество элеменнтов в списке!
    """

    cnt, elem = [], []
    j = 1
    for i in range(len(arr) - 1):
        if arr[i] == arr[i + 1]:
            j += 1
        else:
            cnt.append(j)
            elem.append(arr[i])
            j = 1

    cnt.append(j)
    elem.append(arr[-j])

    return list(zip(elem, cnt))


def get_gmt_flow(phg: str, gmt_flow: dict, start_date: str):
    """ Создание динамики по ГМТ для каждого ПХГ
    """

    data = gmt_flow[phg]

    arr_in = np.array([])
    arr_out = np.array([])

    start_date = pd.to_datetime(start_date, format="%d-%m-%Y")
    init_month = start_date.month - 1

    for year in data:
        days = list(map(lambda x: monthrange(int(year), x + 1)[1],
                    range(init_month, 12)))
        arr_in = np.append(arr_in, np.repeat(data[year]['in'][init_month:], days))
        arr_out = np.append(arr_out, np.repeat(data[year]['out'][init_month:], days))
        init_month = 0

    return arr_in, arr_out


def put_inside(list1, list2):
    """Распределение элементов list2 среди элементов list1.
    """

    n = len(list1) // len(list2)
    for i in range(len(list2)):
        list1.insert((n + 1) * (i + 1) - 1, list2[i])

    return list1


def put_inside_(list1, list2):
    """Распределение элементов list2 среди элементов list1.
    """

    m = len(list1)
    n = len(list2)

    if m % n != 0:
        raise Exception('Длина массаива list1 не кратна list2')

    k = m // n + 1
    for i in range(n):
        list1.insert((k - 1) + k * i, list2[i])

    return list1


def forecast(df, col_name:str, start_date:str, end_date:str):
    """ Формирование блока прогнозных значений за период отбора по ПХГ
    ГПЭ (Газпром Экспорт)
    """

    dev = 1_000_000

    df0 = df[[col_name]].copy()

    start_date = pd.to_datetime(start_date, format='%d-%m-%Y')
    end_date = pd.to_datetime(end_date, format='%d-%m-%Y')

    df0['Дата'] = pd.date_range(start=start_date, end=end_date, freq='D')

    df0['Y'] = df0['Дата'].dt.year
    df0['Q'] = df0['Дата'].dt.quarter
    df0['M'] = df0['Дата'].dt.month

    df0 = df0.set_index('Дата')

    df_year = df0.groupby(['Y'])[col_name].sum() / dev
    df_quarter = df0.groupby(['Y', 'Q'])[col_name].sum() / dev
    df_month = df0.groupby(['Y', 'Q', 'M'])[col_name].sum() / dev
    del df0

    year = start_date.year
    values = put_inside(df_month[year].to_list(), df_quarter[year].to_list())
    values.insert(0, df_year[year])
    values += df_year.loc[year + 1:].to_list()

    return values


def create_temp_(years: list, init_date):
    """ Шаблон для прогнозных оценок.
    """

    init_month = pd.to_datetime(init_date, format-'%d-%m-%Y').month - 1

    # Наимнование меток для прогнозных оценок для следующего года
    labels = get_month_q_label()

    return [years[0]] + labels[init_month:] + years[1:]


def create_temp(years: list, init_date: str):
    """ Шаблон для прогнозных оценок.
    """

    init_month = pd.to_datetime(init_date, format='%d-%m-%Y').month - 1

    # Наимнование меток для прогнозных оценок для следующего года
    labels = get_month_q_label()

    if 0 <= init_month <= 2:
        return [years[0]] + labels[init_month:] + years[1:]
    elif 3 <= init_month <= 5:
        return [years[0]] + labels[1 + init_month:] + years[1:]
    elif 6 <= init_month <= 8:
        return [years[0]] + labels[2 + init_month:] + years[1:]
    else:
        return [years[0]] + labels[3 + init_month:] + years[1:]


def add_balance_to_init_data(params_phg: dict):
    """ Добавление агрегированных данных по балансу.
    """

    for value in params_phg.values():
        value['balance'] = value['balance_gpe'] + value['balance_gmt']

    return params_phg


def split_params(params_phg: dict):
    """ Создание двух словарей с парааметрамаи
    """

    params_phg = add_balance_to_init_data(params_phg)

    params_gmt_gpe = {}
    params = {}
    for key, param in params_phg.items():
        params_gmt_gpe[key] = {}
        params[key] = {}
        for par, value in param.items():
            if par in ['balance_gpe', 'balance_gmt']:
                params_gmt_gpe[key][par] = value
            else:
                params[key][par] = value

    return params_gmt_gpe, params


def add_zeros_to_exceed_month(df, start_date: str):
    """ Добавление нулей в отсутствующие месяца в
    таблицу прогнозных значений!
    """


    month = pd.to_datetime(start_date, format='%d-%m-%Y').month - 1

    if not month:
        return df

    labels = get_month_q_label()

    if 0 < month <= 2:
        k = 0
    elif 3 <= month <= 5:
        k = 1
    elif 6 <= month <= 8:
        k = 2
    else:
        k = 3

    ncol = len(df.columns)
    add_zero_rows = pd.DataFrame(np.repeat(0, ncol * (month + k)).reshape((month + k), ncol),
                                index=labels[:(month + k)], columns=df.columns)

    return pd.concat([df[:1], add_zero_rows, df[1:]], axis=0)


def get_month_q_label():
    """ Список наменований месяцев и кварталов
    """
    
    return ['Январь', 'Февраль', 'Март', '1_квартал',
              'Апрель', 'Май', 'Июнь', '2_квартал',
              'Июль', 'Август', 'Сентябрь', '3_квартал',
              'Октябрь', 'Ноябрь', 'Декабрь', '4_квартал'
              ]
