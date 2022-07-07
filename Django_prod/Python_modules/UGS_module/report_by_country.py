#!/usr/bin/env python

import pandas as pd
import shelve
import Python_modules.UGS_module.functions.functions_for_report as fc

import Python_modules.UGS_module.params.read_params as rp
import Python_modules.UGS_module.params.check_params as cp

def main():
    """ Формировиние части итогового отчета по сранам
    """

    pm = cp.main()
    if not pm:
        sys.exit()

    country_phg = pm.country_phg

    # Файл с прогнозными данными и распределением по направлением
    try:
        with shelve.open('dbl', 'r') as db:
            df_in = db['phg_in']
            df_out = db['phg_out']
    except FileNotFoundError:
        sys.exit("Файлы с данными не найдены!")

    fc.check_on_delete_phg_from_country(country_phg, df_in.columns)

    # Закачка, отбор по странам. Формирование шаблона отчета!
    df_country_in = fc.get_country_massive(df_in, country_phg)
    df_country_out = fc.get_country_massive(df_out, country_phg)

    df_country_in.insert(0, "Закачка, всего", df_country_in.sum(axis=1))
    df_country_out.insert(0, "Отбор, всего", df_country_out.sum(axis=1))
    df_country_in = df_country_in.T
    df_country_out = fc.add_zeros_to_df(df_country_out).T

    df_country_in.index = fc.get_index_list("in", country_phg)
    df_country_out.index = fc.get_index_list("out", country_phg)

    df_country_in = fc.set_first_column(df_country_in)
    df_country_out = fc.set_first_column(df_country_out)

    # Аггргирование данных
    df = pd.concat([df_country_in.append(pd.Series(dtype='float64'),
                                        ignore_index=True), df_country_out],
										axis=0)
    del df_country_in, df_country_out

    df = df.round(1)

    with shelve.open('dbl') as db:
        db['report_by_country'] = df

    print("Отчет по странам готов!")

if __name__ == "__main__":
    import sys
    sys.exit(main())
