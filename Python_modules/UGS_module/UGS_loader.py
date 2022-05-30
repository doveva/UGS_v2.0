"""
Модуль выгрузки данных в формате json для обработки в модуле отчёта ПХГ
"""

from apps.home.models import Points_out, UGS_names, Points_in
import os
import json
"""
def loader(data: dict, UGS: UGS_names, UGS_name: str) -> dict:
    points_value_out = Points_out.objects.filter(name_id=UGS.id).values_list("X", "Y")
    points_value_in = Points_in.objects.filter(name_id=UGS.id).values_list("X", "Y")
    X_range = []
    Y_range = []
    for (x, y) in points_value_in:
        X_range.append(x)
        Y_range.append(y)
    data_in = {"x": X_range, "y": Y_range}
    X_range = []
    Y_range = []
    for (x, y) in points_value_out:
        X_range.append(x)
        Y_range.append(y)
    data_out = {"x": X_range, "y": Y_range}
    wrapper = {}
    wrapper["tech_in"] = data_in
    wrapper["tech_out"] = data_out
    data[UGS_name] = wrapper
    return
"""