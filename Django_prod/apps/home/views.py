# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from Python_modules.Django_modules import model_handler
from Python_modules.UGS_module import UGS_loader


@login_required(login_url="/login/")
def index(request):
    context = {'segment': 'index'}

    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))


# Функция рендера страницы (комментарии к каждой странице отдельно)
# request - переменная запроса к серверу
# context - словарь переменных и значений для передачи в html из python
@login_required(login_url="/login/")
def pages(request, context={}):
    """

    :param request:
    :param context:
    :return: Loads page
    """
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:
        load_template = request.path.split('/')[-1]
        # Загрузка админки
        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        context['segment'] = load_template
        if not load_template == "":
            html_template = loader.get_template('home/' + load_template)
        # Загрузка страницы добавления кривых ПХГ
        if load_template == "ugs_add.html":
            return model_handler.curve_add_loader(request, html_template, context)
        # Загрузка страницы отображения графиков ПХГ
        elif load_template == "ugs_charts.html":
            return model_handler.curve_graph(request, html_template, context)
        # Загрузка страницы настроек модели
        elif load_template == "ugs_settings.html":
            return model_handler.model_create(request, html_template, context)
        # Загрузка страницы подгрузки модели
        elif load_template == "model_load.html":
            return model_handler.model_load(request, html_template, context)
        elif load_template == "repairs.html":
            return model_handler.load_repairs(request, html_template, context)
        elif load_template == "optimization_module.html":
            return model_handler.optimiztion_module(request, html_template, context)

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))
