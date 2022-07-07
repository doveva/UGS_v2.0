def Try_parse(string_value: str, type_parse="int"):
    """
    Функция аналогичная функции C# TryParse. Может принимать в себя список
         Флаг type_parse имеет следующие параметры:
        int - возвращает целочисленное значение
       float - возвращает дробное значение
      list_int - возвращает список целочисленных значений
     list_float - возвращает список дробных значений

    :param string_value: Значение для парсинга
    :param type_parse: Строковое значение типа введённых данных
    :return: Возвращает значение
     строки после парсинга или исходное значение, а также boolean значение успешности парсинга
    """
    if type_parse == "int":
        try:
            result_value = int(string_value)
            result_check = False
        except ValueError:
            result_value = string_value
            result_check = True
    elif type_parse == "float":
        try:
            result_value = float(string_value)
            result_check = False
        except ValueError:
            result_value = string_value
            result_check = True
    elif type_parse == "list_int":
        try:
            result_value = [int(value) for value in string_value]
            result_check = False
        except ValueError:
            result_value = string_value
            result_check = True
    elif type_parse == "list_float":
        try:
            result_value = [float(value) for value in string_value]
            result_check = False
        except ValueError:
            result_value = string_value
            result_check = True

    return result_value, result_check

def date_converter(date_usa: str, type_flag = None):
    date_array = date_usa.split("-")
    if type_flag == "start":
        return "01" + "-" + date_array[1] + "-" + date_array[0]
    elif type_flag == "end":
        return "31" + "-" + "12" + "-" + date_array[0]
    else:
        return date_array[2] + "-" + date_array[1] + "-" + date_array[0]

