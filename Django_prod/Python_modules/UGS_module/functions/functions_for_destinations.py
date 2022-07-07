#!/usr/bin/env python
import numpy as np
import pandas as pd

def add_values_to_label(arr):
    """ Добавление в массив записей
    """

    s = ' '
    arr.extend([
                s * 2 + 'Закачка газа',
                s * 2 + 'Отбор газа',
                s * 4 + 'из него газ, прообретенный вне РФ, всего',
                s * 4 + 'из него, в рамках сделок РЕПО, всего',
                s * 1])


def distr_phg_to_direction(df, weights):
    """ Словарь ПХГ по направлениям с учетов весов распределения!
    """

    direction_phg = {}
    for key in df:
        weight = weights[key]
        direction_phg[key] = \
            pd.DataFrame(np.array(df[key].to_numpy()[:, np.newaxis]) * np.array(list(weight.values())),
                 columns=weight.keys(), index=df.index)

    return direction_phg


def get_country_massive(df, dict_):
    """  Массив данных по странам/направлениям: закачка и отбор:
    df - DataFrame, dict_ - словарь соответсвий: ПХГ -> страны
    """

    df0 = pd.DataFrame([])
    for direct, phg in dict_.items():
        df0[direct] = df.loc[:, phg].sum(axis=1)

    return df0


def set_first_column(df, label='Показатель'):
    """ Переименование индекса в колонку
    """

    return df.reset_index().rename(columns={'index':label})


def add_values_to_df(df, m, n, value, idx):
    """ Добавление m сторок длинны n значений value в DataFrame
        с инлексами idx
    """

    for i in range(m):
        df = pd.concat([df, pd.Series([value] * n, index=idx)], axis=1)

    return df


def add_zeros_to_exceed_month(df, start_date: str):
    """ Добавление нулей в отсутствующие месяца в
    таблицу прогнозных значений!
    """
    
    
    month = pd.to_datetime(start_date, format='%d-%m-%Y').month - 1
    
    if not month:
        return df
    
    labels = ['январь', 'февраль', 'март', '1_квартал',
        'апрель', 'май', 'июнь', '2_квартал',
        'июль', 'август', 'сентябрь', '3_квартал',
        'октябрь', 'ноябрь', 'декабрь', '4_квартал'
        ]
    
    ncol = len(df.columns)
    add_zero_rows = pd.DataFrame(np.repeat(0, ncol * month).reshape(month, ncol),
                                index=labels[:month], columns=df.columns)

    return pd.concat([df[:1], add_zero_rows, df[1:]], axis=0)
