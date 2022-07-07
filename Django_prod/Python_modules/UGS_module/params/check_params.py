#!/usr/bin/env python
import Python_modules.UGS_module.params.test_params as test
import Python_modules.UGS_module.params.read_params as rp
import sys

def main():
    """Проверка параметров модели!
    """

    params = rp.Params()

    check = 0
    # Проверка весов
    check += test.test_weights(params.weights_in)
    check += test.test_weights(params.weights_out)

    # Проверка внутримесячных распределений
    check += test.test_intra_month(params.intra_month)

    # Проверка распределения потоков
    check += test.test_flows(params.flows)

    # Прорверка функций производительности
    check += test.test_functions(params.functions)

    # Проверка параметров ПХГ
    check += test.test_params(params.params_phg)

    # Проверка распределения ГМТ
    check += test.test_gmt(params.gmt)

    # Проверка распределения по месяцам данных
    check += test.test_intra_month_vs_flows(params.intra_month, params.flows)

    # Проверка формата даты
    check += test.test_dates(params.date['start_date'], params.date['end_date'])
    
    # Проверка технической возможности
    check += test.test_tech_availability(params.tech_availability)

    if check == 0:
        return params
    else:
        sys.exit("Нужно проверить параметры: значения некорректны!")

    return

if __name__ == "__main__":
    import sys
    main()
