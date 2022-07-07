#!/usr/bin/env python
import numpy as np
import pandas as pd
import shelve

import Python_modules.UGS_module.functions.functions_for_destinations as fd
import Python_modules.UGS_module.params.read_params as rp
import Python_modules.UGS_module.params.check_params as cp

def main():
    """ Формитрование части итогового отчетв по направлениям
    """

    pm = cp.main()
    if not pm:
        sys.exit()
 
    try:
        # Файл с прогнозными данными и распределением по направлением
        with shelve.open('dbl', 'r') as db:
            df_in = db['phg_in']
            df_out = db['phg_out']
    except FileNotFoundError:
        sys.exit("Файлы с данными не надены!")

    weights_in = pm.weights_in
    weights_out = pm.weights_out
    
    phg_to_geo = {}
    directions = []
    for k, v in weights_in.items():
        phg_to_geo[k] = list(v.keys())
        directions.extend(list(v.keys()))
    directions = np.unique(directions)

    geo_to_phg = {}
    for direct in directions:
        arr = []
        for key, val in phg_to_geo.items():
            if direct in val:
                arr.append(key)
        geo_to_phg[direct] = arr
    del arr

    # Суммы по направлениям
    df_direction_in = fd.get_country_massive(df_in, geo_to_phg)
    df_direction_out = fd.get_country_massive(df_out, geo_to_phg)

    # Распределение ПХГ по направлениям 
    distr_phg_in = fd.distr_phg_to_direction(df_in, weights_in)
    distr_phg_out = fd.distr_phg_to_direction(df_out, weights_out)

    # Формирование итоговой формы
    df, idx = pd.DataFrame([]), []
    index = df_in.index
    n = len(index)
    for geo, phg in geo_to_phg.items():

        df = fd.add_values_to_df(df, 2, n, None, index)

        df = pd.concat([df, df_direction_in[geo]], axis=1)
        df = pd.concat([df, df_direction_out[geo]], axis=1)

        df = fd.add_values_to_df(df, 2, n, 0, index)
        df = fd.add_values_to_df(df, 1, n, None, index)

        idx.append(geo)
        idx.append('ВСЕГО')
        fd.add_values_to_label(idx)

        for p in phg:
            df = fd.add_values_to_df(df, 1, n, None, index)

            df = pd.concat([df, distr_phg_in[p][geo]], axis=1)
            df = pd.concat([df, distr_phg_out[p][geo]], axis=1)

            df = fd.add_values_to_df(df, 2, n, 0, index)
            df = fd.add_values_to_df(df, 1, n, None, index)

            idx.append(p)
            fd.add_values_to_label(idx)

    df = df.T
    df.index = idx
    df = df.astype(float)
    df = df.round(1)
    df = fd.set_first_column(df)

    with shelve.open('dbl', 'c') as db:
        db['report_by_destination'] = df

    print("Отчет по направлениям готов!")

if __name__ == "__main__":
    import sys
    sys.exit(main())
