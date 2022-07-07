# -*- coding: utf-8 -*-
"""
Модуль для обработки запросов рендера различных страниц
"""
# Служебные библиотеки
import datetime
import os
import json
import shutil
from urllib import parse
from zipfile import ZipFile
# Модули работы с Django
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.utils.encoding import smart_str
from apps.home.models import Points_out, UGS_names, Points_in, UGS_settings
from calendar import monthrange
# Служебные библиотеки дополнительные
from Python_modules.Functions.Converters import *
# Модуль расчётный (модуль Алексадра Шерченкова)
from Python_modules.UGS_module import main as Calc_main


# Загрузка страницы добавления кривой ПХГ
# context["number"] - число точек отбора
# context["number_in"] - число точек закачки
# context["name"] - название ПХГ
# context["range_out"] - итерируемый массив по числу точек отбора (в Джанго нельзя создать массив в HTML)
# context["range_in"] - итерируемый массив по числу точек закачки (в Джанго нельзя создать массив в HTML)
def curve_add_loader(request, html_template, context: dict):
    """
    Функция для рендера страницы добаления/изменения кривых ПХГ в базе данных

    :param request: Рендер запроса от front-end
    :param html_template: Шаблон Django для рендера (ugs_add.html)
    :param context: Словарь, передающий параметры на страницу рендера
    :return: Рендер страницы html_template, отправляемой пользователю с учётом параметров
    """
    # Блок создания объектов для заполнения
    if not request.POST.get("pointsnumber") is None:
        if not request.POST.get("UGS") == "":
            name = request.POST.get("UGS")
            points_number = request.POST.get("pointsvalue")
            points_number_in = request.POST.get("pointsvalue_in")
            context['name'] = name
            if not points_number is "":
                if not UGS_names.objects.filter(name=name).exists():
                    p = UGS_names(name=name)
                    p.save()
                context["number"] = int(points_number)
                context["number_in"] = int(points_number_in)
                if context["number"] <= 12:
                    context["range_out"] = list(range(1, context["number"] + 1))
                elif context["number"] <= 0:
                    context["number"] = 0
                    context["range_out"] = list(range(0))
                else:
                    context["number"] = 12
                    context["range_out"] = list(range(1, 13))

                if context["number_in"] <= 12:
                    context["range_in"] = list(range(1, context["number_in"] + 1))
                elif context["number_in"] <= 0:
                    context["number_in"] = 0
                    context["range_in"] = list(range(0))
                else:
                    context["number_in"] = 12
                    context["range_in"] = list(range(1, 13))
                context["max_range"] = list(range(1, max(len(context["range_in"]), len(context["range_out"])) + 1))
    # Блок сохранения введённых значений
    # На данный момент при наличии в базе значений производится перезапись
    elif not request.POST.get("submit_line") is None:
        name = request.POST.get("UGS")
        if not name == "":
            name_id = UGS_names.objects.get(name=name)
            for i in list(range(1, 13)):
                try:
                    X_value_out = float(request.POST.get("Xout" + str(i) + "_value").replace(",", "."))
                    Y_value_out = float(request.POST.get("Yout" + str(i) + "_value").replace(",", "."))
                    if 0 <= X_value_out <= 1 and 0 <= Y_value_out <= 1:
                        if i == 1:
                            if Points_out.objects.filter(name=name_id).exists():
                                Points_out.objects.filter(name=name_id).delete()
                                p = Points_out(X=X_value_out, Y=Y_value_out, name=name_id)
                                p.save()
                            else:
                                p = Points_out(X=X_value_out, Y=Y_value_out, name=name_id)
                                p.save()
                        else:
                            p = Points_out(X=X_value_out, Y=Y_value_out, name=name_id)
                            p.save()
                    try:
                        X_value_in = float(request.POST.get("Xin" + str(i) + "_value").replace(",", "."))
                        Y_value_in = float(request.POST.get("Yin" + str(i) + "_value").replace(",", "."))
                        if 0 <= X_value_in <= 1 and 0 <= Y_value_in <= 1:
                            if i == 1:
                                if Points_in.objects.filter(name=name_id).exists():
                                    Points_in.objects.filter(name=name_id).delete()
                                    p = Points_in(X=X_value_in, Y=Y_value_in, name=name_id)
                                    p.save()
                                else:
                                    p = Points_in(X=X_value_in, Y=Y_value_in, name=name_id)
                                    p.save()
                            else:
                                p = Points_in(X=X_value_in, Y=Y_value_in, name=name_id)
                                p.save()
                    except:
                        continue
                except:
                    try:
                        X_value_in = float(request.POST.get("Xin" + str(i) + "_value").replace(",", "."))
                        Y_value_in = float(request.POST.get("Yin" + str(i) + "_value").replace(",", "."))
                        if 0 <= X_value_in <= 1 and 0 <= Y_value_in <= 1:
                            if i == 1:
                                if Points_in.objects.filter(name=name_id).exists():
                                    Points_in.objects.filter(name=name_id).delete()
                                    p = Points_in(X=X_value_in, Y=Y_value_in, name=name_id)
                                    p.save()
                            else:
                                p = Points_in(X=X_value_in, Y=Y_value_in, name=name_id)
                                p.save()
                    except:
                        break
    else:
        context["number"] = 0
        context["number_in"] = 0
    return HttpResponse(html_template.render(context, request))


# Загрузка графиков
# context["UGS_nm"] - выгрузка массива названий ПХГ из базы
# context["data_out"] - выгрузка массива точек по отбору из ПХГ в формате под JavaScript
# context["data_in"] - выгрузка массива точек по закачке из ПХГ в формате под JavaScript
# context["data_name"] - выгрузка названия выбранного ПХГ для графиков
def curve_graph(request, html_template, context: dict):
    """
    Функция создания вэб-страницы с графиками зависимостей закачки и отбора из ПХГ от заполнения

    :param request: Рендер запроса от front-end
    :param html_template: Шаблон Django для рендера (ugs_chart.html)
    :param context: Словарь, передающий параметры на страницу рендера
    :return: Рендер страницы, отправляемой пользователю с учётом параметров
    """
    U_names = []
    for name in UGS_names.objects.all():
        U_names.append(name.name)
        context["UGS_nm"] = list(U_names)
    if request.method == "POST":
        # Выполнение запроса по отображению графиков отбора и закачки
        if not request.POST.get("submit_chart") is None:
            ugs_name = request.POST.get("UGS_select")
            ugs_obj = UGS_names.objects.filter(name=ugs_name)[0].id
            points_value_out = Points_out.objects.filter(name=ugs_obj).values_list("X", "Y")
            points_value_in = Points_in.objects.filter(name=ugs_obj).values_list("X", "Y")
            data_in = [{"x": x, "y": y} for (x, y) in points_value_in]
            data_out = [{"x": x, "y": y} for (x, y) in points_value_out]
            context["data_out"] = data_out
            context["data_in"] = data_in
            context["data_name"] = ugs_name
    return HttpResponse(html_template.render(context, request))


def model_create(request, html_template, context: dict):
    """
    Функция работы со страницей модели
    :param request: Параметр запроса, требуемый для рендера
    :param html_template: HTML-шиблон для подгрузки
    :param context: словарь для передачи значений из Python во фронтенд
    :return: повторно производит рендер для исправления ошибок, либо открывает новую страниц для сохранения модели
    """

    UGS_names_list = []
    year_list = []
    UGS_params = {}
    for name in UGS_names.objects.all():
        UGS_names_list.append(name.name)
        UGS_params[name.name] = [False, False, False, False, False]
    # Стандартные параметры для страницы
    # Названия ПХГ из базы
    context["UGS_first"] = UGS_names_list[0]
    context["UGS_names"] = UGS_names_list
    # Названия направлений
    context["directions"] = ["Северный поток", "Северный поток 2", "Кондратки", "Велке Капушаны", "Турецкий поток"]
    context["number"] = len(context["directions"])
    context["number_range"] = range(context["number"])
    # Названия месяцев
    context["months"] = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август",
                         "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]
    context["month_range"] = range(12)
    context["data_check"] = UGS_params

    # Проверка блокировки значения
    if "model_block" not in list(context.keys()):
        # Установка блока на данные
        context["model_block"] = True
    functions = {}
    params_phg = {}
    weights_in = {}
    weights_out = {}
    flows = {}
    gmt = {}
    GPE_balance = {}
    GMT_balance = {}
    params_coef = {}


    if request.method == "POST":
        # Обработка кнопки "Сохранить модель"
        if not request.POST.get("Submit_settings") is None:
            year_first = request.POST.get("year_first")
            year_last = request.POST.get("year_last")
            for i in range(int(year_last) - int(year_first) + 1):
                year_list.append(int(year_first) + i)

            flows_in = {}
            flows_out = {}
            gmt_in = {}
            gmt_out = {}
            month_data = {}
            year_data = {}
            days_data = {}
            days_range_data = {}
            data_check = {}
            model_complete = True

            for UGS in UGS_names_list:
                # Словарь для сохранения значений проверки
                UGS_check = [True, True, True, True, True]

                # Проверка значений параметров
                capacity = UGS_settings.objects.filter(name__name=UGS).values_list()[0][2]
                volume_in = UGS_settings.objects.filter(name__name=UGS).values_list()[0][3]
                volume_out = UGS_settings.objects.filter(name__name=UGS).values_list()[0][4]
                balance_gpe, balance_gpe_check = Try_parse(request.POST.get("main_settings_" + UGS + "(GPE_balance)"),
                                                           "float")
                balance_gmt, balance_gmt_check = Try_parse(request.POST.get("main_settings_" + UGS + "(GMT_balance)"),
                                                           "float")
                params_in, params_in_check = Try_parse(request.POST.get("main_settings_" + UGS + "(in_coef)"),
                                                       "float")
                params_out, params_out_check = Try_parse(request.POST.get("main_settings_" + UGS + "(out_coef)"),
                                                         "float")

                if volume_in > capacity or volume_out > capacity or capacity < 0 or volume_out < 0 or volume_in < 0:
                    UGS_check[1] = False
                    model_complete = False
                elif balance_gmt_check or balance_gpe_check or params_in_check or params_out_check:
                    UGS_check[1] = False
                    model_complete = False
                elif balance_gmt > capacity or balance_gpe > capacity:
                    UGS_check[1] = False
                    model_complete = False
                elif params_in < 0 or params_in > 1:
                    UGS_check[1] = False
                    model_complete = False
                elif params_out < 0 or params_out > 1:
                    UGS_check[1] = False
                    model_complete = False

                # Считывание параметров объёма ПХГ, максимального объёма закачки и отбора, а также баланса ПХГ
                params_phg[UGS] = {"capacity": capacity,
                                   "volume_in": volume_in,
                                   "volume_out": volume_out,
                                   "balance_gpe": balance_gpe,
                                   "balance_gmt": balance_gmt}

                # Проверка значений кривых
                points_in_x = [point_in[2] for point_in in Points_in.objects.filter(name__name=UGS).values_list()]
                points_in_y = [point_in[3] for point_in in Points_in.objects.filter(name__name=UGS).values_list()]
                points_out_x = [point_out[2] for point_out in Points_out.objects.filter(name__name=UGS).values_list()]
                points_out_y = [point_out[3] for point_out in Points_out.objects.filter(name__name=UGS).values_list()]
                for point_in_x in points_in_x:
                    if point_in_x < 0 or point_in_x > 1:
                        UGS_check[0] = False
                        model_complete = False
                    else:
                        UGS_check[0] = True
                for point_in_y in points_in_y:
                    if point_in_y < 0 or point_in_y > 1:
                        UGS_check[0] = False
                        model_complete = False
                for point_out_x in points_out_x:
                    if point_out_x < 0 or point_out_x > 1:
                        UGS_check[0] = False
                        model_complete = False
                for point_out_y in points_out_y:
                    if point_out_y < 0 or point_out_y > 1:
                        UGS_check[0] = False
                        model_complete = False

                # Считывание функций отбора и закачки в ПХГ
                functions[UGS] = {"in": {"x": points_in_x,
                                         "y": points_in_y},
                                  "out": {"x": points_out_x,
                                          "y": points_out_y}}
                # Считывание и весов
                weights_in[UGS], temp_check = Try_parse(request.POST.getlist
                                                        ("main_settings_Дамборжице(weights_in_f" + UGS), "list_float")
                if temp_check:
                    UGS_check[1] = False
                    model_complete = False
                elif not sum(weights_in[UGS]) == 1:
                    UGS_check[1] = False
                    model_complete = False

                weights_out[UGS], temp_check = Try_parse(request.POST.getlist
                                                         ("main_settings_Дамборжице(weights_out_f" + UGS), "list_float")
                if temp_check:
                    UGS_check[1] = False
                    model_complete = False
                elif not sum(weights_out[UGS]) == 1:
                    UGS_check[1] = False
                    model_complete = False

                # Считывание потоков отбора и закачки, а также потока ГМТ
                year_flow = {}
                year_gmt = {}
                for year in year_list:
                    # Проверка значений потока ГПЕ
                    year_in_flow, temp_check = Try_parse(request.POST.getlist("GPE_in_" + str(year) + "_" + UGS),
                                                         "list_int")
                    if temp_check:
                        UGS_check[3] = False
                        model_complete = False

                    year_out_flow, temp_check = Try_parse(request.POST.getlist("GPE_out_" + str(year) + "_" + UGS),
                                                          "list_int")
                    if temp_check:
                        UGS_check[3] = False
                        model_complete = False

                    year_flow[year] = {"in": year_in_flow,
                                       "out": year_out_flow}

                    # Проверка значений потока ГМТ
                    year_in_gmt, temp_check = Try_parse(request.POST.getlist("GMT_in_" + str(year) + "_" + UGS),
                                                        "list_int")
                    if temp_check:
                        UGS_check[4] = False
                        model_complete = False

                    year_out_gmt, temp_check = Try_parse(request.POST.getlist("GMT_out_" + str(year) + "_" + UGS),
                                                         "list_int")
                    if temp_check:
                        UGS_check[4] = False
                        model_complete = False

                    year_gmt[year] = {"in": year_in_gmt,
                                      "out": year_out_gmt}
                flows[UGS] = year_flow
                gmt[UGS] = year_gmt
                # Разделение in и out массивов для рендера
                year_flow_in = {}
                year_flow_out = {}
                year_gmt_in = {}
                year_gmt_out = {}

                years_m_daily = {}
                years_d_daily = {}
                years_dr_daily = {}
                years_f_daily = []
                for year in year_list:
                    year_flow_in[str(year)] = list(map(int, flows[UGS][year]["in"]))
                    year_flow_out[str(year)] = list(map(int, flows[UGS][year]["out"]))
                    year_gmt_in[str(year)] = list(map(int, gmt[UGS][year]["in"]))
                    year_gmt_out[str(year)] = list(map(int, gmt[UGS][year]["out"]))
                    # Заполнение месячных данных по закачке/отбору
                    month_list = []
                    days_list = {}
                    days_values_range = {}
                    for i in range(len(year_flow_in[str(year)])):
                        if year_flow_in[str(year)][i] == year_flow_out[str(year)][i] and year_flow_in[str(year)][i] == \
                                1:
                            month_list.append(context["months"][i])
                            days_values_list = {}
                            days_array = []
                            for day in range(1, monthrange(int(year), int(i + 1))[1] + 1):
                                days_array.append(datetime.date(int(year), i + 1, day).strftime("%d.%m.%Y"))

                            days_values_range[context["months"][i]] = days_array

                            for day in range(1, monthrange(int(year), int(i + 1))[1] + 1):
                                inflow_temp = request.POST.get(
                                    "flow_direction_in_" + str(year) + "_" + context["months"][i] + "_" + datetime.date(
                                        int(year), i + 1, day).strftime("%d.%m.%Y") + "_" + UGS)
                                outflow_temp = request.POST.get(
                                    "flow_direction_out_" + str(year) + "_" + context["months"][
                                        i] + "_" + datetime.date(int(year), i + 1, day).strftime(
                                        "%d.%m.%Y") + "_" + UGS)

                                if inflow_temp == None or outflow_temp == None:
                                    days_values_list[datetime.date(int(year), i + 1, day).strftime("%d.%m.%Y")] = [0, 0]
                                    UGS_check[4] = False
                                    model_complete = False
                                else:
                                    inflow_temp, temp_check = Try_parse(inflow_temp, "float")
                                    if temp_check:
                                        UGS_check[4] = False
                                        model_complete = False

                                    outflow_temp, temp_check = Try_parse(outflow_temp, "float")
                                    if temp_check:
                                        UGS_check[4] = False
                                        model_complete = False

                                    days_values_list[datetime.date(int(year), i + 1, day).strftime("%d.%m.%Y")] = \
                                        [outflow_temp, inflow_temp]

                            days_list[context["months"][i]] = days_values_list
                    if not len(month_list) == 0:
                        years_m_daily[str(year)] = month_list
                        years_f_daily.append(str(year))
                        years_d_daily[str(year)] = days_list
                        years_dr_daily[str(year)] = days_values_range

                flows_in[UGS] = year_flow_in
                flows_out[UGS] = year_flow_out
                gmt_in[UGS] = year_gmt_in
                gmt_out[UGS] = year_gmt_out

                month_data[UGS] = years_m_daily
                year_data[UGS] = years_f_daily
                days_data[UGS] = years_d_daily
                days_range_data[UGS] = years_dr_daily

                GPE_balance[UGS] = params_phg[UGS]["balance_gpe"]
                GMT_balance[UGS] = params_phg[UGS]["balance_gmt"]
                params_coef[UGS] = [params_in, params_out]

                # Запись значений обратно в форму
                context[UGS + "_in_weights"] = weights_in[UGS]
                context[UGS + "_out_weights"] = weights_out[UGS]

                data_check[UGS] = UGS_check

            # Отправка данных во фронтенд
            context["params_phg"] = params_phg
            context["functions"] = functions
            context["weights_in"] = weights_in
            context["weights_out"] = weights_out

            context["GPE_months"] = month_data
            context["GPE_years"] = year_data
            # Заполнение основных параметров
            context["GPE_balance"] = GPE_balance
            context["GMT_balance"] = GMT_balance
            context["prod_coef"] = params_coef
            context["params_flag"] = request.POST.get("main_settings_(calc_type)")
            # Заполнение потоков ГПЭ
            context["flows_in"] = flows_in
            context["flows_out"] = flows_out
            # Заполнение потоков ГМТ
            context["gmt_in"] = gmt_in
            context["gmt_out"] = gmt_out

            context["dates"] = [request.POST.get("date_first"), request.POST.get("date_last")]
            context["years"] = year_list
            context["days"] = days_data
            context["days_range"] = days_range_data

            context["data_check"] = data_check
            context["model_block"] = False

            # Запуск создания JSON
            if model_complete:
                try:
                    context["model_name"] = request.POST.get("model_name")
                except:
                    context["model_name"] = ""

                json_dumper(context, request)
                html_template = loader.get_template("home/model_complete.html")
                context["enable_download"] = False
                context["model_status"] = False
                HttpResponse(html_template.render(context, request))

        # Обработка кнопки "Создать шаблон модели"
        elif not request.POST.get("Submit_dates") is None:
            start_date = request.POST.get("date_first")
            end_date = request.POST.get("date_last")
            checkbox = request.POST.get("param_flag")
            if checkbox == "with":
                context["params_flag_value"] = True
                prod_coef = {}
                for UGS in UGS_names_list:
                    prod_coef[UGS] = [1, 1]
            else:
                context["params_flag_value"] = False
                prod_coef = {}
                for UGS in UGS_names_list:
                    if UGS == "Реден":
                        prod_coef[UGS] = [0.9, 0.9]
                    elif UGS == "Бергермеер":
                        prod_coef[UGS] = [0.7, 0.7]
                    else:
                        prod_coef[UGS] = [1, 1]

            start_year = start_date.split("-")[0]
            year_list.append(int(start_year))
            for i in range(int(end_date.split("-")[0]) - int(start_year)):
                start_year = int(start_year) + 1
                year_list.append(int(start_year))

            # Считывание дат и годов
            context["dates"] = [start_date, end_date]
            context["years"] = year_list

            # Базовые веса на закачку
            context["Дамборжице_in_weights"] = [0.4, 0.5, 0.1, 0, 0]
            context["Катарина_in_weights"] = [0.3, 0.5, 0.2, 0, 0]
            context["Реден_in_weights"] = [0.5, 0.3, 0.2, 0, 0]
            context["Хайдах_in_weights"] = [0, 0, 0, 1, 0]
            context["Бергермеер_in_weights"] = [0.5, 0.4, 0.1, 0, 0]

            # Базовые веса на отбор
            context["Дамборжице_out_weights"] = [0.4, 0.5, 0.1, 0, 0]
            context["Катарина_out_weights"] = [0.3, 0.5, 0.2, 0, 0]
            context["Реден_out_weights"] = [0.5, 0.3, 0.2, 0, 0]
            context["Хайдах_out_weights"] = [0, 0, 0, 1, 0]
            context["Бергермеер_out_weights"] = [0.5, 0.4, 0.1, 0, 0]

            year_in_flow = {}
            year_out_flow = {}
            year_in_gmt = {}
            year_out_gmt = {}

            flows_in = {}
            flows_out = {}
            gmt_in = {}
            gmt_out = {}
            GPE_month = {}
            UGS_check = {}
            production_coef = {}

            # Формирование базовых значений формы
            for UGS in UGS_names_list:
                UGS_check[UGS] = [True, False, True, True, True]
                # Базовый набор параметров для потоков и GMT
                for year in year_list:
                    year_in_flow[str(year)] = [0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0]
                    year_out_flow[str(year)] = [1, 1, 1, 0, 0, 0, 1, 1, 0, 1, 1, 1]
                    year_in_gmt[str(year)] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                    year_out_gmt[str(year)] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

                flows_in[str(UGS)] = year_in_flow
                flows_out[str(UGS)] = year_out_flow
                gmt_in[str(UGS)] = year_in_gmt
                gmt_out[str(UGS)] = year_out_gmt
                if UGS == "Бергермеер":
                    production_coef[str(UGS)] = [0.7, 0.7]
                elif UGS == "Реден":
                    production_coef[str(UGS)] = [0.9, 0.9]
                else:
                    production_coef[str(UGS)] = [1, 1]

                # Формирование базовых значений для баансов ПХГ и ГМТ
                GPE_balance[str(UGS)] = ""
                GMT_balance[str(UGS)] = 0
                GPE_month[str(UGS)] = []

            context["prod_coef"] = production_coef
            context["data_check"] = UGS_check
            context["flows_in"] = flows_in
            context["flows_out"] = flows_out
            context["gmt_in"] = gmt_in
            context["gmt_out"] = gmt_out
            context["GPE_balance"] = GPE_balance
            context["GMT_balance"] = GMT_balance
            context["GPE_years"] = GPE_month

            context["model_block"] = False

        elif not request.POST.get("model_start") is None:
            # Считывание название модели
            model_name = request.POST.get("model_name")
            context["model_name"] = model_name
            # Запуск модуля Саши
            try:
                Calc_main.main()
                context["enable_download"] = True
                context["model_status"] = True
                context["error_message"] = "Расчёт выполнен!"
            except Exception as msg:
                context["enable_download"] = False
                context["model_status"] = True
                context["error_message"] = msg

            html_template = loader.get_template("home/model_complete.html")
            return HttpResponse(html_template.render(context, request))

        elif not request.POST.get("model_download") is None:
            model_name = request.POST.get("model_name")
            # Сохранение JSON
            save_path = os.path.join(os.getcwd(), "Python_modules", "Models_database", model_name + ".json")
            file_path = os.path.join(os.getcwd(), "Python_modules", "UGS_module", "json_data", "params_model.json")
            shutil.copy(file_path, save_path)

            # Создание zip архива для передачи пользователю
            file_zip = os.path.join("Python_modules", "UGS_module", "download", "data.zip")
            if os.path.exists(file_zip):
                os.remove(file_zip)
            data_path = os.path.join("Python_modules", "UGS_module", "report")
            with ZipFile(file_zip, 'w') as zip:
                for path, directories, files in os.walk(data_path):
                    for file in files:
                        file_name = os.path.join(path, file)
                        zip.write(file_name)

            # Скачивание файла результатов
            with open(file_zip, "rb") as file_download:
                response = HttpResponse(file_download.read(), content_type='application/zip')
                response['Content-Disposition'] = 'attachment; filename="result_data.zip"'
                return response
        else:
            return HttpResponse(html_template.render(context, request))

    else:
        pass

    return HttpResponse(html_template.render(context, request))


def json_dumper(context: dict, request):
    """
    Функция создания JSON файла для модуля ПХГ

    :param context: словарь из бэкэнда для формирования JSON файла
    :return: создание JSON файла модели
    """
    path = os.path.join(os.getcwd(), "Python_modules", "UGS_module", "json_data", "params_model.json")
    json_data = {}
    intra_month = {}
    flows = {}
    gmt = {}
    weights_in = {}
    weights_out = {}
    availability_params = {}

    for UGS in context["days"]:
        flow = {}
        flow_gmt = {}
        for years in context["years"]:
            flow[str(years)] = {"in": context["flows_in"][UGS][str(years)],
                                "out": context["flows_out"][UGS][str(years)]}
            flow_gmt[str(years)] = {"in": context["gmt_in"][UGS][str(years)],
                                    "out": context["gmt_out"][UGS][str(years)]}
        flows[UGS] = flow
        gmt[UGS] = flow_gmt
        availability_params[UGS] = {"in": context["prod_coef"][UGS][0],
                                    "out": context["prod_coef"][UGS][1]}
        days_month = {}
        for years in context["days"][UGS]:
            months = {}
            for month in context["days"][UGS][years]:
                daily_values = []
                for days in context["days"][UGS][years][month]:
                    daily_values.append(float(context["days"][UGS][years][month][days][1]) - float(
                        context["days"][UGS][years][month][days][0]))
                months[str(context["months"].index(month) + 1)] = daily_values
            days_month[years] = months
        intra_month[UGS] = days_month
        temp_UGS_in_directions = {}
        temp_UGS_out_directions = {}

        for i in range(len(context["directions"])):
            if not context["weights_in"][UGS][i] == 0:
                temp_UGS_in_directions[context["directions"][i]] = context["weights_in"][UGS][i]
            if not context["weights_out"][UGS][i] == 0:
                temp_UGS_out_directions[context["directions"][i]] = context["weights_out"][UGS][i]

        weights_in[UGS] = temp_UGS_in_directions
        weights_out[UGS] = temp_UGS_out_directions

    json_data["intra_month"] = intra_month
    json_data["params_phg"] = context["params_phg"]
    json_data["tech_availability"] = availability_params
    json_data["functions"] = context["functions"]
    json_data["flows"] = flows
    json_data["gmt"] = gmt
    json_data["weights_in"] = weights_in
    json_data["weights_out"] = weights_out
    json_data["country_phg"] = {"Австрия": ["Хайдах"],
                                "Германия": ["Катарина", "Реден"],
                                "Сербия": ["Банатский_двор"],
                                "Нидерланды": ["Бергермеер"],
                                "Чехия": ["Дамборжице"]}
    json_data["date"] = {"start_date": date_converter(context["dates"][0], "start"),
                         "end_date": date_converter(context["dates"][1], "end"),
                         "current_date": datetime.datetime.today().strftime("%d-%m-%Y")}
    json_data["user"] = request.user.username
    with open(path, "wb") as outfile:
        encoded = json.dumps(json_data, ensure_ascii=False, indent=4).encode("utf-8")
        outfile.write(encoded)


def model_load(request, html_template, context: dict):
    """
    Функция для обработки страницы загрузки модели

    :param request: Запрос на рендер
    :param html_template: Шаблон для рендера
    :param context: Словарь, передаваемый во фронтенд
    :return: Рендер страницы
    """
    model_path = os.path.join(os.getcwd(), "Python_modules", "Models_database")
    model_names = []
    models = {}
    for root, dirs, files in os.walk(model_path):
        for file in files:
            model_names.append(file.replace(".json", ""))
            model_meta = {}
            model_meta["user"] = json.load(open(os.path.join(root, file), encoding="utf-8"))["user"]
            model_meta["date"] = datetime.datetime.fromtimestamp(os.path.getctime(os.path.join(root, file))).strftime(
                "%d-%m-%Y")
            models[model_names[-1]] = model_meta

    context["model_names"] = model_names
    context["model_meta"] = models
    if request.method == "POST":
        if not request.POST.get("model_load") is None:
            model_name = request.POST.get("model_load")
            context = load_json(os.path.join(os.getcwd(), "Python_modules", "Models_database", model_name + ".json"))
            html_template = loader.get_template("home/ugs_settings.html")
            return model_create(request, html_template, context)

        elif not request.POST.get("model_delete") is None:
            model_name = request.POST.get("model_delete")
            if os.path.exists(os.path.join(os.getcwd(), "Python_modules", "Models_database", model_name + ".json")):
                os.remove(os.path.join(os.getcwd(), "Python_modules", "Models_database", model_name + ".json"))
                return HttpResponseRedirect("/model_load.html")
            else:
                return HttpResponseRedirect("/model_load.html")
        else:
            html_template = loader.get_template("home/ugs_settings.html")
            return model_create(request, html_template, context)

    return HttpResponse(html_template.render(context, request))


def load_json(path: str):
    """
    Функция обеспечивающая загрузку JSON в формат для отправки во фронтенд

    :param path: String значение пути до файла модели в формате JSON
    :return: Dictionary context для работы с фронтендом
    """
    context: dict
    context = {}
    data = json.load(open(path, encoding="utf-8"))
    context["model_name"] = path.split("\\")[-1].split(".")[0]
    context["directions"] = ["Северный поток", "Северный поток 2", "Кондратки", "Велке Капушаны", "Турецкий поток"]
    context["months"] = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август",
                         "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]
    context["month_range"] = range(12)

    context["params_phg"] = data["params_phg"]
    context["UGS_names"] = list(data["params_phg"].keys())
    context["UGS_first"] = context["UGS_names"][0]
    context["functions"] = data["functions"]

    context["model_block"] = False
    context["dates"] = [date_converter(data["date"]["start_date"]), date_converter(data["date"]["end_date"])]
    context["years"] = range(int(context["dates"][0].split("-")[0]), int(context["dates"][1].split("-")[0]) + 1)
    context["data_check"] = {}
    # Словари потоков ГПЕ
    context["flows_out"] = {}
    context["flows_in"] = {}
    # Словари потоков ГМТ
    context["gmt_in"] = {}
    context["gmt_out"] = {}
    # Словари баланса
    context["GPE_balance"] = {}
    context["GMT_balance"] = {}
    # Словарь коэффициентов ограничений
    context["prod_coef"] = {}
    # Словари для суточных значений
    context["days"] = {}
    context["days_range"] = {}
    context["GPE_years"] = {}
    context["GPE_months"] = {}
    for UGS in context["UGS_names"]:
        context["data_check"][UGS] = [False, False, False, False, False]
        context["GPE_balance"][UGS] = data["params_phg"][UGS]["balance_gpe"]
        context["GMT_balance"][UGS] = data["params_phg"][UGS]["balance_gmt"]
        context[UGS + "_in_weights"] = []
        context[UGS + "_out_weights"] = []
        for direction in context["directions"]:
            try:
                context[UGS + "_in_weights"].append(data["weights_in"][UGS][direction])
            except KeyError:
                context[UGS + "_in_weights"].append(0)
            try:
                context[UGS + "_out_weights"].append(data["weights_out"][UGS][direction])
            except KeyError:
                context[UGS + "_out_weights"].append(0)

        context["prod_coef"][UGS] = [data["tech_availability"][UGS]["in"], data["tech_availability"][UGS]["out"]]
        if not context["prod_coef"][UGS][0] == 1 or context["prod_coef"][UGS][1] == 1:
            context["params_flag_value"] = True
        flow_in = {}
        flow_out = {}
        gmt_in = {}
        gmt_out = {}
        for year in context["years"]:
            flow_in[str(year)] = data["flows"][UGS][str(year)]["in"]
            flow_out[str(year)] = data["flows"][UGS][str(year)]["out"]
            gmt_in[str(year)] = data["gmt"][UGS][str(year)]["in"]
            gmt_out[str(year)] = data["gmt"][UGS][str(year)]["out"]

        context["flows_in"][UGS] = flow_in
        context["flows_out"][UGS] = flow_out
        context["gmt_in"][UGS] = gmt_in
        context["gmt_out"][UGS] = gmt_out

        # Конвертация дат
        years_flows = {}
        years_flows_data = {}
        GPE_years = []
        GPE_months = {}
        for year in list(data["intra_month"][UGS].keys()):
            year_flows = {}
            year_flows_data = {}
            GPE_years.append(year)
            GPE_months_value = []
            for month in list(data["intra_month"][UGS][year].keys()):
                month_flows = []
                month_flows_data = {}
                GPE_months_value.append(context["months"][int(month) - 1])
                for index, day_value in enumerate(list(data["intra_month"][UGS][year][month])):
                    month_flows.append(datetime.datetime(int(year), int(month), index + 1).strftime("%d.%m.%Y"))
                    if day_value < 0:
                        month_flows_data[datetime.datetime(int(year), int(month), index + 1).strftime("%d.%m.%Y")] \
                            = [day_value, 0.0]
                    else:
                        month_flows_data[datetime.datetime(int(year), int(month), index + 1).strftime("%d.%m.%Y")] \
                            = [0.0, day_value]

                year_flows[context["months"][int(month) - 1]] = month_flows
                year_flows_data[context["months"][int(month) - 1]] = month_flows_data

            years_flows[year] = year_flows
            years_flows_data[year] = year_flows_data
            GPE_months[year] = GPE_months_value

        # Запись значения
        context["GPE_years"][UGS] = GPE_years
        context["GPE_months"][UGS] = GPE_months
        context["days_range"][UGS] = years_flows
        context["days"][UGS] = years_flows_data

    return context

def load_repairs(request, html_template, context: dict):
    UGS_names_list = []
    for name in UGS_names.objects.all():
        UGS_names_list.append(name.name)
    context["UGS_names"] = UGS_names_list
    context["models"] = [x.replace(".json", "") for x in os.listdir(os.path.join(os.getcwd(),"Python_modules", "Models_database"))]
    return HttpResponse(html_template.render(context, request))

def optimiztion_module(request, html_template, context: dict):
    # TBD
    return HttpResponse(html_template.render(context, request))