#!/usr/bin/env python
# -*- coding: utf-8 -*-

import shelve
import pandas as pd
import Python_modules.UGS_module.params.check_params as cp
import Python_modules.UGS_module.functions.functions_for_forecasting as ff


def main():

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

    # Начальная и последняя дата прогноза
    start_date = pm.date['start_date']
    end_date = pm.date['end_date']

    # Агркгация и разбиение параметров ГМТ и ГПЭ
    params_gpe_gmt, params = ff.split_params(ff.add_balance_to_init_data(params))
    columns = ['Год', 'Месяц', 'Тех. закачка', 'Факт. Закачка ГПЭ', 'Тех. отбор', 'Факт. Отбор ГПЭ', 'Баланс']

    # Параметры снижения закачки/отбора
    decrease = {"Катарина": 0.91, "Хайдах": 1, "Дамборжице": 1, "Реден": 1, "Бергермеер": 1}

    # Заполнение динамики по ПХГ
    df0 = pd.DataFrame([])
    for phg in params: # params
        koeff_decrease = decrease[phg]
        while True:
            try:
                data = ff.get_dynamics(phg, functions, flows, params, intra_month, gmt, koeff_decrease)
            except Exception as msg:
                sys.exit(msg)
            else:
                df = pd.DataFrame(dict(zip(columns, data)))

            # Добавление динамики по ГМТ
            gmt_in, gmt_out = ff.get_gmt_flow(phg, gmt)

            # Дополнительные колонки
            df['Факт. Закачка ГМТ'] = gmt_in
            df['Факт. Отбор ГМТ'] = gmt_out
            df['Баланс_ГМТ'] = params_gpe_gmt[phg]['balance_gmt'] + (gmt_in - gmt_out).cumsum()
            df['Баланс_ГПЭ'] = df['Баланс'] - df['Баланс_ГМТ']
            
            if (df['Баланс_ГПЭ'] <= 0).any():
                koeff_decrease -= 0.01
            else:
                break
            if koeff_decrease <= 0:
                break
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
    df_in = pd.DataFrame(forecast_in, index=ff.create_temp(years))
    df_out = pd.DataFrame(forecast_out, index=ff.create_temp(years))

    # Сохранение объектов в файл!
    with shelve.open('dbl', 'c') as db:
        db['phg_in'] = df_in
        db['phg_out'] = df_out

    # Сохранение данных
    writer = pd.ExcelWriter('report/Динамика_прогнозных_значений.xlsx', engine='xlsxwriter')
    try:
        df0.to_excel(writer, sheet_name='ПХГ')
        df_in.to_excel(writer, sheet_name='Прогноз_закачки')
        df_out.to_excel(writer, sheet_name='Прогноз_отбора')
        writer.save()
        print("\nДинамика расчитана!")
    except:
        raise BlockingIOError("Невозможно сохранить дынные в файл!")

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
