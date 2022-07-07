#!/usr/bin/env python
# -*- coding: utf-8 -*-

import shelve
import os
import pandas as pd
import Python_modules.UGS_module.params.check_params as cp
import Python_modules.UGS_module.functions.functions_for_forecasting as ff
from Python_modules.UGS_module.functions.exceptions import UserException
import Python_modules.UGS_module.formatting_dynamics as fd


def main():
    """ Расчет прогнозных значений закачки/отбюора газа для ПХГ
    """

    # Чтение и проверка параметров
    pm = cp.main()
    if not pm:
        sys.exit()

    # Параметры ПХГ
    functions = pm.functions
    flows = pm.flows
    gmt = pm.gmt
    params = pm.params_phg
    intra_month = pm.intra_month
    tech_availability = pm.tech_availability

    # Начальная и последняя дата прогноза
    start_date = pm.date['start_date']
    end_date = pm.date['end_date']

    # Агркгация и разбиение параметров ГМТ и ГПЭ
    params_gpe_gmt, params = ff.split_params(ff.add_balance_to_init_data(params))
    columns = ['Год', 'Месяц', 'Тех. закачка', 'Факт. Закачка ГПЭ', 'Тех. отбор', 'Факт. Отбор ГПЭ', 'Баланс']

    # Заполнение динамики по ПХГ
    df0 = pd.DataFrame([])
    for phg in params:
        koeff_decrease = 1
        while True:
            try:
                data = ff.get_dynamics(phg, functions, flows, params, intra_month,
                                        gmt, tech_availability, start_date, koeff_decrease)
            except UserException as msg:
                print(msg)
                koeff_decrease -= 0.05
                print(f"Коэффициент снижен до {koeff_decrease: 0.2f}")
            except Exception as msg:
                sys.exit(msg)
            else:
                df = pd.DataFrame(dict(zip(columns, data)))
                break
            if koeff_decrease <= 0:
                sys.exit("Алгоритм не срошелся!\nПроверить корректность входных параметров!")

        # Добавление динамики по ГМТ
        gmt_in, gmt_out = ff.get_gmt_flow(phg, gmt, start_date)

        # Дополнительные колонки
        df['Факт. Закачка ГМТ'] = gmt_in
        df['Факт. Отбор ГМТ'] = gmt_out
        df['Баланс_ГМТ'] = params_gpe_gmt[phg]['balance_gmt'] + \
            (gmt_in - gmt_out).cumsum()
        df['Баланс_ГПЭ'] = params_gpe_gmt[phg]['balance_gpe'] + \
            (df['Факт. Закачка ГПЭ'] - df['Факт. Отбор ГПЭ']).cumsum()

        # Корректировка балансов ГМЭ и ГМТ: при снижении объемов до нуля ГПЭ, отбор производится из ГМТ!
        df['Баланс_ГМТ'] = df['Баланс_ГМТ'].where(df['Баланс_ГПЭ'] > 0,
                                        df.loc[:, ['Баланс_ГМТ', 'Баланс_ГПЭ']][df['Баланс_ГПЭ'] < 0].sum(axis=1))
        df['Баланс_ГПЭ'] = df['Баланс_ГПЭ'].where(df['Баланс_ГПЭ'] > 0, 0)

        df0 = pd.concat([df0, df], axis=1)
    del df

    columns.extend(['Факт. Закачка ГМТ', 'Факт. Отбор ГМТ', 'Баланс_ГМТ', 'Баланс_ГПЭ'])

    # Добвление агрегированных данных
    df = pd.DataFrame([])
    df['Год'] = df0.iloc[:, 0]
    df['Месяц'] = df0.iloc[:, 1]
    for col in columns[2:]:
        df[col] = df0[col].sum(axis=1)
    df0 = pd.concat([df0, df], axis=1)
    del df

    phg_labels = list(params.keys())
    phg_labels.append('Итого_ПХГ')
    df0.columns = pd.MultiIndex.from_product([phg_labels, columns], names=['ПХГ', 'Показатели'])

    # Прогнозные значения Отбора и Закачки по ГПЭ
    forecast_in, forecast_out = {}, {}
    for key in params:
        forecast_in[key] = ff.forecast(df0[key], 'Факт. Закачка ГПЭ', start_date=start_date, end_date=end_date)
        forecast_out[key] = ff.forecast(df0[key], 'Факт. Отбор ГПЭ', start_date=start_date, end_date=end_date)

    # Прогноз закачки и отбора газа по ГПЭ
    years = list(map(lambda x : str(x), range(int(start_date[-4:]), int(end_date[-4:]) + 1)))
    index_ = ff.create_temp(years, start_date)

    df_in = pd.DataFrame(forecast_in, index=index_)
    df_out = pd.DataFrame(forecast_out, index=index_)

    # Добавление нулей в отсутствующие месяцы
    # в таблицу прогнозных значений
    df_in = ff.add_zeros_to_exceed_month(df_in, start_date)
    df_out = ff.add_zeros_to_exceed_month(df_out, start_date)

    # Сохранение объектов в файл!
    with shelve.open('dbl', 'c') as db:
        db['phg_in'] = df_in
        db['phg_out'] = df_out

    # Форматирование столбцов: разделитель тысяч, округление до целого целого
    j = 0
    for i in range(len(params) + 1):
        df0.iloc[:, (2 + j):(11 + j)] = \
            df0.iloc[:, (2 + j):(11 + j)].applymap(lambda x: f"{x:,.0f}".replace(',', ' '))
        j += 11


    filename = os.path.join(os.getcwd(), "Python_modules", "UGS_module", "report", 'Динамика_прогнозных_значений.xlsx')
    # Сохранение данных
    writer = pd.ExcelWriter(filename, engine='xlsxwriter')
    try:
        df0.to_excel(writer, sheet_name='ПХГ')
        df_in.to_excel(writer, sheet_name='Прогноз_закачки')
        df_out.to_excel(writer, sheet_name='Прогноз_отбора')
        writer.save()
    except:
        sys.exit("Невозможно сохранить дынные в файл!")

    # Форматирование файла динамики
    fd.main(filename)

    print("\nДинамика расчитана и сохранена!")

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
