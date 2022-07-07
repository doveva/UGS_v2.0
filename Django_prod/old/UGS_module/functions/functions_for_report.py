#!/usr/bin/env python

import numpy as np
import pandas as pd


def fill_template_by_country(text, extended_text=True):
    """Заполнние шаблона по странам.
    text - осовная информация,
    extended_text - отображение дополнительной информации!
    """

    if extended_text:
        return [text + ', всего',
                  "  из него газ, прообретенный вне РФ, всего",
                  "  из него, в рамках сделок РЕПО, всего"
                  ]

    return [text + ', всего']


def get_index_list(flow, country_phg: dict):
    """ Форироваиние списка для именования индекса в df.
    flow - признак закачки (in), отбора (out)
    """

    if flow == 'in':
        label = 'Закачка газа'
        extended_text = False
    elif flow == 'out':
        label = 'Отбор газа'
        extended_text = True
    else:
        raise ValueError('Параметр flow должен быть равен in/out')

    index_for_data = fill_template_by_country(label, extended_text)
    for country in country_phg:
        index_for_data += fill_template_by_country(country, extended_text)

    return index_for_data


def add_zeros_to_df(df, value=0):
    """Добавление полей c к df - DataFrame.
    """

    columns = df.columns
    df0 = pd.DataFrame([])
    for i in range(len(columns)):
        df0[columns[i]] = df.iloc[:, i]
        df0[str(i) + ''] = value
        df0[str(i) + '_'] = value

    return df0


def add_values_to_label(arr):
    """ Добавление в массив arr записей для шаблона.
    """

    s = ' '
    arr.extend([
                s * 2 + 'Закачка газа',
                s * 2 + 'Отбор газа',
                s * 4 + 'из него газ, прообретенный вне РФ, всего',
                s * 4 + 'из него, в рамках сделок РЕПО, всего',
                s * 1])


def distr_phg_to_direction(df, weights: dict):
    """ Формироввание Словарь распределения
    ПХГ по направлениям с учетов весов распределения!
    """

    direction_phg = {}
    for key in df:
        weight = weights[key]
        direction_phg[key] = \
            pd.DataFrame(np.array(df[key][:, np.newaxis]) * np.array(list(weight.values())),
                 columns=weight.keys(), index=df.index)

    return direction_phg


def get_country_massive(df, dict_):
    """  Массив данных по странам/направлениям: закачка и отбор:
    df - DataFrame, dict_ - словарь соответсвий: ПХГ -> страны
    """

    df0 = pd.DataFrame([])
    for direct, phg in dict_.items():
        if phg:
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


def check_on_delete_phg_from_country(country_phg, template):
    """ Удаление ПХГ из словаря страны -> ПХГ
    """

    empty_keys = []
    for direct, phg in country_phg.items():
        for p in phg:
            if p not in template:
                country_phg[direct].remove(p)
                if not country_phg[direct]:
                    empty_keys.append(direct)

    for k in empty_keys: country_phg.pop(k)


