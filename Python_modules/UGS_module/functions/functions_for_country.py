#!/usr/bin/env python
import pandas as pd


def fill_template_by_country(country_name, text, extended_text=True):
    """Заполнние шаблона по странам"""

    if extended_text:
        return [country_name + text,
                  "  из него газ, прообретенный вне РФ, всего",
                  "  из него, в рамках сделок РЕПО, всего"
                  ]

    return [country_name + text]


def add_zeros_to_df(df):
    """Добавление списка нулей к DataFrame"""

    columns = df.columns
    df0 = pd.DataFrame([])
    for i in range(len(columns)):
        df0[columns[i]] = df.iloc[:, i]
        df0[str(i) + ''] = 0
        df0[str(i) + '_'] = 0

    return df0


def get_index_list(label, country_phg, add_text: bool, text=', всего'):
    """ Форироваиние списка для индекса DataFrame
    """

    index_for_data = fill_template_by_country(label, text, add_text)
    for country in country_phg:
        index_for_data += fill_template_by_country(country, text, add_text)

    return index_for_data


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
