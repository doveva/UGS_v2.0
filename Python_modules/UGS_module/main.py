#!/usr/bin/env python
import sys
sys.path.insert(0, 'functions')
sys.path.insert(0, 'params')
import Python_modules.UGS_module.create_report_file as crf
import Python_modules.UGS_module.forecasting as fc
import Python_modules.UGS_module.report_by_country as rc
import Python_modules.UGS_module.report_by_destination as rd

def main():
    print("Расчет...\n")
    # Расчет прогнозных значений закачки/отбора. Формрование файла данных.
    fc.main()
    # Формировиние певрой части итогового отчета по сранам
    rc.main()
    # Формитрование последней части итогового отчетв по направлениям
    rd.main()
    # Создание на основе итоговых отчетов агрегированной формы
    crf.main()

    return 0


if __name__ == "__main__":
    sys.exit(main())
