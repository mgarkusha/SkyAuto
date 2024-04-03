from django.shortcuts import render, render_to_response, get_object_or_404, HttpResponseRedirect
from django.contrib import auth
from django.db.models import Sum, Count, Min, Max
from django.http import Http404
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
import datetime
import calendar
import operator
import re

from infinity.models import TsOrders, Drivers, Corporations, Cars, TsCarstatechanges
from salary.models import Salary
from .models import Gibdd, CompanyPenalty
from .forms import GibddForm, CompanyPenaltyForm


def login(request):
    if request.method == 'POST':
        # print("POST data=", request.POST)
        username = request.POST.get('login')
        password = request.POST.get('password')
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return HttpResponseRedirect('/')
        else:
            return render(request, 'chart.html', {'errors': True})
    raise Http404


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/')


# ----------- ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ И ФУНКЦИИ ------------------------ #
def current_day():
    day = datetime.datetime.today()
    test_day = datetime.datetime.today().replace(year=2017, month=11, day=2)
    # return test_day
    return day


first_day_of_current_month = current_day().replace(day=1, hour=0, minute=0, second=0, microsecond=1)
sum_days_in_month = calendar.monthrange(first_day_of_current_month.year, first_day_of_current_month.month)[1]
last_day_of_current_month = current_day().replace(day=sum_days_in_month, hour=23, minute=59, second=59,
                                                  microsecond=999999)

last_month = first_day_of_current_month - datetime.timedelta(days=1)
first_day_last_month = last_month.replace(day=1, hour=0, minute=0, second=0, microsecond=1)
last_last_month = first_day_last_month - datetime.timedelta(days=1)

second_plus_one = timedelta(seconds=1)
one_day = timedelta(days=1)
one_hour = timedelta(hours=1)
# Изменил на 6 часов :)
two_hour = timedelta(hours=6)


def last_day_of_month(year, month):
    sum_days_in_month_ = calendar.monthrange(datetime.datetime(year=year, month=month, day=1).year,
                                             datetime.datetime(year=year, month=month, day=1).month)[1]
    return sum_days_in_month_


last_day_last_month = datetime.datetime(year=first_day_last_month.year, month=first_day_last_month.month,
                                        day=last_day_of_month(first_day_last_month.year, first_day_last_month.month),
                                        hour=23, minute=59, second=59, microsecond=999999)


def condition_or_0(condition):
    if condition:
        return int(condition)
    else:
        return 0


def format_number(number):
    new_number = '{0:,}'.format(condition_or_0(number)).replace(',', ' ')
    return new_number


# Запрос всех заказов из базы статистики (все с State=7 -оплачен)
def get_orders_range(start_day, end_day):
    orders = TsOrders.objects.using('Cx_TaxiStatistics').filter(deliverytime__range=(start_day, end_day), state=7)
    return orders


# Список водителей, отключенных  от показа (1.Гаркуша и диспетчера)
driver_list_my_block = [5018737745, 5077107426, 5077107390, 5077107396, 5077107402, 5077107408, 5077107414, 5077107420]
driver_list_sn_block = [5042082447, 5011597095, 5017290831]


# Список id работающих водителей из таблицы водителей (isblocked!=1, isdeleted!=1) за исключением driver_list_my_block
def driver_list_work_id():
    id = list([int(i['id']) for i in
               # Drivers.objects.using('Cx_TaxiConfiguration').exclude(isblocked=1).exclude(isdeleted=1).exclude(
               Drivers.objects.using('Cx_TaxiConfiguration').exclude(isdeleted=1).exclude(
                   id__in=driver_list_my_block).values('id')])
    return id


# Основная таблица штрафов ГИБДД
def gibdd(request):
    gibdd_penalties = Gibdd.objects.all().filter(penalty_driver_paid__exact=False).order_by('-date')
    gibdd_marker = True
    context = {'gibdd_marker': gibdd_marker,
               'gibdd_penalties': gibdd_penalties}
    return render(request, 'gibdd.html', context)


# Основная таблица штрафов КОМПАНИИ
def company_penalty(request):
    company_penalties = CompanyPenalty.objects.all().filter(penalty_driver_paid__exact=False).order_by('-date')
    company_penalty_marker = True
    context = {'company_penalty_marker': company_penalty_marker,
               'company_penalties': company_penalties}
    return render(request, 'gibdd.html', context)


# ### !!! ### !!! ### !!! ГИБДД НАЧАЛО !!! ###### !!! ### !!!

# Добавление штрафа ГИБДД #
def gibdd_cu(request, year=None, month=None, day=None, hour=None, minute=None):
    # Инициализация календарика
    if year:
        incident_date = datetime.datetime(year=year, month=month, day=day, hour=hour, minute=minute, second=0,
                                          microsecond=0)
        incident_marker = True
    else:
        incident_date = datetime.datetime.now()
        incident_marker = False

    if request.method == 'POST':
        gibdd_form = GibddForm(request.POST)
        if gibdd_form.is_valid():
            post = gibdd_form.save(commit=False)
            post.date = datetime.date.today()
            post.incident_date = incident_date
            post.incident_decree_date = request.POST.get('incident_decree_date')
            post.incident_number = condition_or_0(request.POST.get('incident_number'))
            if request.POST.get('incident_type'):
                post.incident_type = request.POST.get('incident_type')
            else:
                post.incident_type = 'Нарушение скоростного режима'
            post.incident_speed = condition_or_0(request.POST.get('incident_speed'))
            post.incident_place = request.POST.get('incident_place')
            post.penalty_gibdd = condition_or_0(request.POST.get('penalty_gibdd'))
            post.car_id = re.split(r'_', request.POST.get('idcar_driver_id'))[0]
            post.driver_id = re.split(r'_', request.POST.get('idcar_driver_id'))[1]
            post.speed_recommend = condition_or_0(request.POST.get('speed_recommend'))
            post.penalty_company = condition_or_0(request.POST.get('penalty_company'))
            post.manager_comment = request.POST.get('manager_comment')
            if request.POST.get('penalty_gibdd_paid'):
                post.penalty_gibdd_paid = True
            post.save()
        return HttpResponseRedirect('/gibdd')
    else:
        # ВОДИТЕЛИ И АВТО
        # Cписок водителей и авто в дату нарушения НА ЗАКАЗЕ
        # driver_work_on_orders_list = list([int(i['iddriver']) for i in TsOrders.objects.using('Cx_TaxiStatistics').filter(
        #     starttime__lte=incident_date).filter(finishtime__gte=incident_date).values('iddriver')])
        # print(driver_work_on_orders_list)

        # Запрос списка тачек
        cars = Cars.objects.using('Cx_TaxiConfiguration')
        drivers = Drivers.objects.using('Cx_TaxiConfiguration')

        # for driver_id in driver_list_work_id():
        #     try:
        #         terminal_state = TsCarstatechanges.objects.using('Cx_TaxiStatistics').filter(iddriver=driver_id).filter(
        #             date__range=(incident_date, incident_date)).exclude(terminaltype=5).exclude(state=1).values(
        #             'iddriver', 'idcar', 'date', 'state').order_by('-date')[0]
        #         driver_online_in_incedent_date.append(terminal_state)
        #     except:
        #         continue
        # print(driver_online_in_incedent_date)

        driver_chart = []
        driver_online_in_incedent_date = list()
        for driver_id in driver_list_work_id():
            driver_dict = dict()
            # Cписок водителей и авто в дату нарушения ОНЛАЙН (Все статусы, кроме Офлайн)
            incident_date_minus_2hour = incident_date - two_hour
            try:
                # Берем последний статус водителей за 2 часа назад
                terminal_state = TsCarstatechanges.objects.using('Cx_TaxiStatistics').filter(iddriver=driver_id).filter(
                    date__range=(incident_date_minus_2hour, incident_date)).exclude(terminaltype=5).exclude(
                    state=1).values(
                    'iddriver', 'idcar', 'state', 'date').order_by('-date')[0]
                driver_online_in_incedent_date.append(terminal_state)
            except:
                terminal_state = None
            # /Cписок водителей и авто в дату нарушения ОНЛАЙН (Все статусы, кроме Офлайн)

            driver_dict['fullname'] = Drivers.objects.using('Cx_TaxiConfiguration').get(id=driver_id).fullname
            if terminal_state:
                driver_dict['idcar'] = terminal_state['idcar']
                driver_dict['driver_id'] = driver_id
                try:
                    driver_dict['car_number'] = cars.get(id=terminal_state['idcar']).number
                except:
                    driver_dict['car_number'] = 'Отсутствует'
                driver_dict['state'] = terminal_state['state']
                driver_dict['online'] = True
                driver_dict['date'] = terminal_state['date']
            else:
                try:
                    driver_dict['idcar'] = drivers.get(id=driver_id).iddefaultcar.id
                    driver_dict['car_number'] = cars.get(id=driver_dict['idcar']).number
                except:
                    driver_dict['idcar'] = 0
                    driver_dict['car_number'] = 'Отсутствует'
                driver_dict['driver_id'] = driver_id
                # print(driver_dict['idcar'])
                driver_dict['online'] = False
                driver_dict['date'] = None

            # cars = Cars.objects.using('Cx_TaxiConfiguration').filter(idcurrentdriver=driver_id)
            # if cars:
            #     driver_dict['carmodel'] = cars[0].idmodel.name
            #     driver_dict['number'] = cars[0].number
            #     driver_dict['color'] = cars[0].idcolor.name
            #     driver_dict['online'] = ''
            # driver_dict['online_sort'] = False if '' else True
            # print(driver_dict['online_sort'])
            driver_chart.append(driver_dict)
        # Берем последнего водителя, который сидит в авто. Предпоследнего удаляем.
        for driver_1 in driver_chart:
            for driver_2 in driver_chart:
                if driver_1['date']:
                    if driver_2['date']:
                        if driver_1['idcar'] == driver_2['idcar'] and driver_1['date'] > driver_2['date']:
                            print(driver_2)
                            driver_chart.remove(driver_2)
        # print(driver_online_in_incedent_date)
        # Сортируем по CarNumber
        sort_fullname_chart = []
        for i in sorted(driver_chart, key=operator.itemgetter("car_number")):
            sort_fullname_chart.append(i)
        sort_online_chart = []
        for i in sorted(sort_fullname_chart, key=operator.itemgetter("online"), reverse=True):
            sort_online_chart.append(i)
    context = {'incident_date': incident_date,
               'incident_decree_date': datetime.datetime.now(),
               'incident_marker': incident_marker,
               'driver_chart': sort_online_chart}
    return render(request, 'gibdd_cu.html', context)


# Удаление штрафа ГИБДД
def gibdd_delete(request, gibdd_id):
    gibdd_penalties = get_object_or_404(Gibdd, id=gibdd_id)
    gibdd_penalties.delete()
    return HttpResponseRedirect('/gibdd')


# Редактирование штрафа ГИБДД
def gibdd_update(request, gibdd_id):
    gibdd_penalties = get_object_or_404(Gibdd, id=gibdd_id)

    # !!! Придумай на досуге функцию!!! (нехрен торопить начальству...) !!!
    if request.method == 'POST':
        form = GibddForm(request.POST, instance=gibdd_penalties)
        if form.is_valid():
            post = form.save(commit=False)
            post.incident_date = request.POST.get('incident_date')
            post.incident_decree_date = request.POST.get('incident_decree_date')
            post.incident_number = condition_or_0(request.POST.get('incident_number'))
            if request.POST.get('incident_type'):
                post.incident_type = request.POST.get('incident_type')
            else:
                post.incident_type = 'Нарушение скоростного режима'
            post.incident_speed = condition_or_0(request.POST.get('incident_speed'))
            post.incident_place = request.POST.get('incident_place')
            post.penalty_gibdd = condition_or_0(request.POST.get('penalty_gibdd'))
            post.car_id = re.split(r'_', request.POST.get('idcar_driver_id'))[0]
            post.driver_id = re.split(r'_', request.POST.get('idcar_driver_id'))[1]
            post.speed_recommend = condition_or_0(request.POST.get('speed_recommend'))
            post.penalty_company = condition_or_0(request.POST.get('penalty_company'))
            post.manager_comment = request.POST.get('manager_comment')
            if request.POST.get('penalty_gibdd_paid'):
                post.penalty_gibdd_paid = True
                post.penalty_gibdd_paid_date = datetime.datetime.now()
            else:
                post.penalty_gibdd_paid = False
            post.save()
            return HttpResponseRedirect('/gibdd')
    else:
        cars = Cars.objects.using('Cx_TaxiConfiguration')
        drivers = Drivers.objects.using('Cx_TaxiConfiguration')
        driver_chart = []
        driver_online_in_incedent_date = list()
        for driver_id in driver_list_work_id():
            driver_dict = dict()
            # Cписок водителей и авто в дату нарушения ОНЛАЙН (Все статусы, кроме Офлайн)
            incident_date_minus_2hour = gibdd_penalties.incident_date - two_hour
            try:
                # Берем последний статус водителей за 2 часа назад
                terminal_state = TsCarstatechanges.objects.using('Cx_TaxiStatistics').filter(iddriver=driver_id).filter(
                    date__range=(incident_date_minus_2hour, gibdd_penalties.incident_date)).exclude(
                    terminaltype=5).exclude(
                    state=1).values(
                    'iddriver', 'idcar', 'state', 'date').order_by('-date')[0]
                driver_online_in_incedent_date.append(terminal_state)
            except:
                terminal_state = None
            driver_dict['fullname'] = Drivers.objects.using('Cx_TaxiConfiguration').get(id=driver_id).fullname
            if terminal_state:
                driver_dict['idcar'] = terminal_state['idcar']
                driver_dict['driver_id'] = driver_id
                try:
                    driver_dict['car_number'] = cars.get(id=terminal_state['idcar']).number
                except:
                    driver_dict['car_number'] = 'Отсутствует'
                driver_dict['state'] = terminal_state['state']
                driver_dict['online'] = True
                driver_dict['date'] = terminal_state['date']
            else:
                try:
                    driver_dict['idcar'] = drivers.get(id=driver_id).iddefaultcar.id
                    driver_dict['car_number'] = cars.get(id=driver_dict['idcar']).number
                except:
                    driver_dict['idcar'] = 0
                    driver_dict['car_number'] = 'Отсутствует'
                driver_dict['driver_id'] = driver_id
                # print(driver_dict['idcar'])
                driver_dict['online'] = False
                driver_dict['date'] = None
            if int(gibdd_penalties.driver_id) == driver_id:
                driver_dict['checked'] = True
            driver_chart.append(driver_dict)
        # Берем последнего водителя, который сидит в авто. Предпоследнего удаляем.
        for driver_1 in driver_chart:
            for driver_2 in driver_chart:
                if driver_1['date']:
                    if driver_2['date']:
                        if driver_1['idcar'] == driver_2['idcar'] and driver_1['date'] > driver_2['date']:
                            print(driver_2)
                            driver_chart.remove(driver_2)
        sort_fullname_chart = []
        for i in sorted(driver_chart, key=operator.itemgetter("car_number")):
            sort_fullname_chart.append(i)
        sort_online_chart = []
        for i in sorted(sort_fullname_chart, key=operator.itemgetter("online"), reverse=True):
            sort_online_chart.append(i)
        # !!! Придумай на досуге функцию!!! (нехрен торопить начальству...) !!!

    context = {'date': gibdd_penalties.date,
               'incident_number': gibdd_penalties.incident_number,
               'incident_type': gibdd_penalties.incident_type,
               'incident_speed': gibdd_penalties.incident_speed,
               'incident_place': gibdd_penalties.incident_place,
               'penalty_gibdd': gibdd_penalties.penalty_gibdd,
               'driver_id': gibdd_penalties.driver_id,
               'car_id': gibdd_penalties.car_id,
               'speed_recommend': gibdd_penalties.speed_recommend,
               'penalty_company': gibdd_penalties.penalty_company,
               'manager_comment': gibdd_penalties.manager_comment,
               'penalty_gibdd_paid': gibdd_penalties.penalty_gibdd_paid,
               'penalty_gibdd_paid_date': gibdd_penalties.penalty_gibdd_paid_date,
               'penalty_driver_paid': gibdd_penalties.penalty_driver_paid,
               'incident_date': gibdd_penalties.incident_date,
               'incident_decree_date': gibdd_penalties.incident_decree_date,
               'incident_marker': True,
               'driver_chart': sort_online_chart}
    return render(request, 'gibdd_cu.html', context)


# ### !!! ### !!! ### !!! ГИБДД КОНЕЦ !!! ###### !!! ### !!!


# Добавление штрафа КОМПАНИИ #
def company_penalty_cu(request, year=None, month=None, day=None, hour=None, minute=None, second=None):
    # Инициализация календарика
    if year:
        incident_date = datetime.datetime(year=year, month=month, day=day, hour=hour, minute=minute, second=second,
                                          microsecond=0)
        incident_marker = True
    else:
        incident_date = datetime.datetime.now()
        incident_marker = False

    if request.method == 'POST':
        company_penalty_form = CompanyPenaltyForm(request.POST)
        if company_penalty_form.is_valid():
            post = company_penalty_form.save(commit=False)
            post.date = datetime.date.today()
            post.incident_date = incident_date
            if request.POST.get('incident_type'):
                post.incident_type = request.POST.get('incident_type')
            else:
                post.incident_type = 'Нарушение скоростного режима'
            post.incident_speed = condition_or_0(request.POST.get('incident_speed'))
            post.incident_place = request.POST.get('incident_place')
            post.car_id = re.split(r'_', request.POST.get('idcar_driver_id'))[0]
            post.driver_id = re.split(r'_', request.POST.get('idcar_driver_id'))[1]
            post.speed_recommend = condition_or_0(request.POST.get('speed_recommend'))
            post.penalty_company = condition_or_0(request.POST.get('penalty_company'))
            post.manager_comment = request.POST.get('manager_comment')
            if request.POST.get('penalty_driver_paid'):
                post.penalty_driver_paid = True
                post.penalty_driver_paid_date = datetime.datetime.now()
            post.save()
        return HttpResponseRedirect('/company_penalty')
    else:
        # Запрос списка тачек
        cars = Cars.objects.using('Cx_TaxiConfiguration')
        drivers = Drivers.objects.using('Cx_TaxiConfiguration')

        driver_chart = []
        driver_online_in_incedent_date = list()
        for driver_id in driver_list_work_id():
            driver_dict = dict()
            # Cписок водителей и авто в дату нарушения ОНЛАЙН (Все статусы, кроме Офлайн)
            incident_date_minus_2hour = incident_date - two_hour
            try:
                # Берем последний статус водителей за 5 часов назад
                terminal_state = TsCarstatechanges.objects.using('Cx_TaxiStatistics').filter(iddriver=driver_id).filter(
                    date__range=(incident_date_minus_2hour, incident_date)).exclude(terminaltype=5).exclude(
                    state=1).values('iddriver', 'idcar', 'state', 'date').order_by('-date')[0]
                driver_online_in_incedent_date.append(terminal_state)
            except:
                terminal_state = None
            # /Cписок водителей и авто в дату нарушения ОНЛАЙН (Все статусы, кроме Офлайн)
            driver_dict['fullname'] = Drivers.objects.using('Cx_TaxiConfiguration').get(id=driver_id).fullname
            if terminal_state:
                driver_dict['idcar'] = terminal_state['idcar']
                driver_dict['driver_id'] = driver_id
                try:
                    driver_dict['car_number'] = cars.get(id=terminal_state['idcar']).number
                except:
                    driver_dict['car_number'] = 'Неизвестно'
                driver_dict['state'] = terminal_state['state']
                driver_dict['online'] = True
                driver_dict['date'] = terminal_state['date']
            else:
                driver_dict['driver_id'] = driver_id
                try:
                    driver_dict['idcar'] = drivers.get(id=driver_id).iddefaultcar.id
                    driver_dict['car_number'] = cars.get(id=driver_dict['idcar']).number
                except:
                    driver_dict['idcar'] = 0
                    driver_dict['car_number'] = 'Неизвестно'
                driver_dict['online'] = False
                driver_dict['date'] = None

            driver_chart.append(driver_dict)
        # Берем последнего водителя, который сидит в авто. Предпоследнего удаляем.
        for driver_1 in driver_chart:
            for driver_2 in driver_chart:
                if driver_1['date']:
                    if driver_2['date']:
                        if driver_1['idcar'] == driver_2['idcar'] and driver_1['date'] > driver_2['date']:
                            print(driver_2)
                            driver_chart.remove(driver_2)
        # Сортируем по CarNumber
        sort_fullname_chart = []
        for i in sorted(driver_chart, key=operator.itemgetter("car_number")):
            sort_fullname_chart.append(i)
        sort_online_chart = []
        for i in sorted(sort_fullname_chart, key=operator.itemgetter("online"), reverse=True):
            sort_online_chart.append(i)
    context = {'incident_date': incident_date,
               'incident_decree_date': datetime.datetime.now(),
               'incident_marker': incident_marker,
               'driver_chart': sort_online_chart}
    return render(request, 'company_penalty_cu.html', context)


def company_penalty_update(request, company_penalty_id):
    company_penalty = get_object_or_404(CompanyPenalty, id=company_penalty_id)

    # !!! Придумай на досуге функцию!!! (нехрен торопить начальству...) !!!
    if request.method == 'POST':
        form = CompanyPenaltyForm(request.POST, instance=company_penalty)
        if form.is_valid():
            post = form.save(commit=False)
            post.incident_date = request.POST.get('incident_date')
            if request.POST.get('incident_type'):
                post.incident_type = request.POST.get('incident_type')
            else:
                post.incident_type = 'Нарушение скоростного режима'
            post.incident_speed = condition_or_0(request.POST.get('incident_speed'))
            post.incident_place = request.POST.get('incident_place')
            post.car_id = re.split(r'_', request.POST.get('idcar_driver_id'))[0]
            post.driver_id = re.split(r'_', request.POST.get('idcar_driver_id'))[1]
            post.speed_recommend = condition_or_0(request.POST.get('speed_recommend'))
            post.penalty_company = condition_or_0(request.POST.get('penalty_company'))
            post.manager_comment = request.POST.get('manager_comment')
            if request.POST.get('penalty_driver_paid'):
                post.penalty_driver_paid = True
                post.penalty_driver_paid_date = datetime.datetime.now()
            else:
                post.penalty_driver_paid = False
            post.save()
            return HttpResponseRedirect('/company_penalty')
    else:
        cars = Cars.objects.using('Cx_TaxiConfiguration')
        drivers = Drivers.objects.using('Cx_TaxiConfiguration')
        driver_chart = []
        driver_online_in_incedent_date = list()
        for driver_id in driver_list_work_id():
            driver_dict = dict()
            # Cписок водителей и авто в дату нарушения ОНЛАЙН (Все статусы, кроме Офлайн)
            incident_date_minus_2hour = company_penalty.incident_date - two_hour
            try:
                # Берем последний статус водителей за 2 часа назад
                terminal_state = TsCarstatechanges.objects.using('Cx_TaxiStatistics').filter(iddriver=driver_id).filter(
                    date__range=(incident_date_minus_2hour, company_penalty.incident_date)).exclude(
                    terminaltype=5).exclude(
                    state=1).values(
                    'iddriver', 'idcar', 'state', 'date').order_by('-date')[0]
                driver_online_in_incedent_date.append(terminal_state)
            except:
                terminal_state = None
            driver_dict['fullname'] = Drivers.objects.using('Cx_TaxiConfiguration').get(id=driver_id).fullname
            if terminal_state:
                driver_dict['idcar'] = terminal_state['idcar']
                driver_dict['driver_id'] = driver_id
                driver_dict['car_number'] = cars.get(id=terminal_state['idcar']).number
                driver_dict['state'] = terminal_state['state']
                driver_dict['online'] = True
                driver_dict['date'] = terminal_state['date']
            else:
                try:
                    driver_dict['idcar'] = drivers.get(id=driver_id).iddefaultcar.id
                    driver_dict['car_number'] = cars.get(id=driver_dict['idcar']).number
                except:
                    driver_dict['idcar'] = 0
                    driver_dict['car_number'] = 'Отсутствует'
                driver_dict['driver_id'] = driver_id
                # print(driver_dict['idcar'])
                driver_dict['online'] = False
                driver_dict['date'] = None
            if int(company_penalty.driver_id) == driver_id:
                driver_dict['checked'] = True
            driver_chart.append(driver_dict)
        # Берем последнего водителя, который сидит в авто. Предпоследнего удаляем.
        for driver_1 in driver_chart:
            for driver_2 in driver_chart:
                if driver_1['date']:
                    if driver_2['date']:
                        if driver_1['idcar'] == driver_2['idcar'] and driver_1['date'] > driver_2['date']:
                            print(driver_2)
                            driver_chart.remove(driver_2)
        sort_fullname_chart = []
        for i in sorted(driver_chart, key=operator.itemgetter("car_number")):
            sort_fullname_chart.append(i)
        sort_online_chart = []
        for i in sorted(sort_fullname_chart, key=operator.itemgetter("online"), reverse=True):
            sort_online_chart.append(i)
        # !!! Придумай на досуге функцию!!! (нехрен торопить начальству...) !!!

    context = {'date': company_penalty.date,
               'incident_type': company_penalty.incident_type,
               'incident_speed': company_penalty.incident_speed,
               'incident_place': company_penalty.incident_place,
               'driver_id': company_penalty.driver_id,
               'car_id': company_penalty.car_id,
               'speed_recommend': company_penalty.speed_recommend,
               'penalty_company': company_penalty.penalty_company,
               'manager_comment': company_penalty.manager_comment,
               'penalty_driver_paid': company_penalty.penalty_driver_paid,
               'incident_date': company_penalty.incident_date,
               'incident_marker': True,
               'driver_chart': sort_online_chart}
    return render(request, 'company_penalty_cu.html', context)


def company_penalty_delete(request, company_penalty_id):
    company_penalties = get_object_or_404(CompanyPenalty, id=company_penalty_id)
    company_penalties.delete()
    return HttpResponseRedirect('/company_penalty')


def gibdd_company_stat(request, in_driver_id=None):
    # Список id работающих водителей из таблицы водителей (isblocked!=1)
    driver_list_work_id = list([int(i['id']) for i in
                                Drivers.objects.using('Cx_TaxiConfiguration').exclude(isblocked=1).exclude(
                                    isdeleted=1).exclude(id__in=driver_list_my_block).exclude(
                                    id__in=driver_list_sn_block).values('id')])

    car = Cars.objects.using('Cx_TaxiConfiguration')
    gibdd_penalties = Gibdd.objects.all().order_by('-date')
    company_penalties = CompanyPenalty.objects.all().order_by('-date')

    # ЧАРТ С ВОДИТЕЛЯМИ
    drivers_chart = []
    for driver_id in driver_list_work_id:
        driver_dict = dict()
        driver_dict['driver_id'] = driver_id
        driver_dict['fullname'] = Drivers.objects.using('Cx_TaxiConfiguration').get(id=driver_id).fullname
        company_open = company_penalties.filter(driver_id=driver_id).filter(
            penalty_driver_paid=False).count()
        driver_dict['company_open'] = company_open
        driver_dict['company_close'] = company_penalties.filter(driver_id=driver_id).filter(
            penalty_driver_paid=True).count()
        gibdd_open = gibdd_penalties.filter(driver_id=driver_id).filter(penalty_gibdd_paid=False).count()
        driver_dict['gibdd_open'] = gibdd_open
        driver_dict['gibdd_close'] = gibdd_penalties.filter(driver_id=driver_id).filter(
            penalty_gibdd_paid=True).count()
        driver_dict['total_count'] = company_penalties.filter(driver_id=driver_id).count() + gibdd_penalties.filter(
            driver_id=driver_id).count()
        driver_dict['total_rub'] = condition_or_0(
            company_penalties.filter(driver_id=driver_id).aggregate(Sum('penalty_company'))[
                'penalty_company__sum']) + condition_or_0(
            gibdd_penalties.filter(driver_id=driver_id).aggregate(Sum('penalty_gibdd'))['penalty_gibdd__sum'])
        driver_dict['total_open'] = company_open + gibdd_open
        drivers_chart.append(driver_dict)

    sort_fullname_drivers_chart = []
    for i in sorted(drivers_chart, key=operator.itemgetter("fullname")):
        sort_fullname_drivers_chart.append(i)

    sort_drivers_chart = []
    for i in sorted(sort_fullname_drivers_chart, key=operator.itemgetter("total_open"), reverse=True):
        sort_drivers_chart.append(i)

    # ЧАРТ ГИБДД ВОДИТЕЛЯ
    gibdd_penalties_chart = []
    for penalty in gibdd_penalties.filter(driver_id=in_driver_id):
        gibdd_penalties_dict = dict()
        gibdd_penalties_dict['id'] = penalty.id
        gibdd_penalties_dict['date'] = penalty.date
        gibdd_penalties_dict['incident_date'] = penalty.incident_date
        gibdd_penalties_dict['incident_decree_date'] = penalty.incident_decree_date
        gibdd_penalties_dict['penalty_gibdd_paid'] = penalty.penalty_gibdd_paid
        gibdd_penalties_dict['penalty_gibdd_paid_date'] = penalty.penalty_gibdd_paid_date
        try:
            gibdd_penalties_dict['car_callsign'] = car.get(id=penalty.car_id).callsign
            gibdd_penalties_dict['car_model'] = car.get(id=penalty.car_id).idmodel.name
            gibdd_penalties_dict['car_number'] = car.get(id=penalty.car_id).number
        except:
            gibdd_penalties_dict['car_callsign'] = ''
            gibdd_penalties_dict['car_model'] = 'Нет данных'
            gibdd_penalties_dict['car_number'] = ''
        gibdd_penalties_dict['incident_type'] = penalty.incident_type
        gibdd_penalties_dict['incident_speed'] = penalty.incident_speed
        gibdd_penalties_dict['speed_recommend'] = penalty.speed_recommend
        gibdd_penalties_dict['incident_place'] = penalty.incident_place
        gibdd_penalties_dict['manager_comment'] = penalty.manager_comment
        gibdd_penalties_dict['penalty_gibdd'] = penalty.penalty_gibdd
        gibdd_penalties_dict['penalty_driver_paid_date'] = penalty.penalty_driver_paid_date
        gibdd_penalties_dict['penalty_driver_paid'] = penalty.penalty_driver_paid
        gibdd_penalties_chart.append(gibdd_penalties_dict)

    # ЧАРТ КОМПАНИИ ВОДИТЕЛЯ
    company_penalties_chart = []
    for penalty in company_penalties.filter(driver_id=in_driver_id):
        company_penalties_dict = dict()
        company_penalties_dict['id'] = penalty.id
        company_penalties_dict['date'] = penalty.date
        try:
            company_penalties_dict['car_callsign'] = car.get(id=penalty.car_id).callsign
            company_penalties_dict['car_model'] = car.get(id=penalty.car_id).idmodel.name
            company_penalties_dict['car_number'] = car.get(id=penalty.car_id).number
        except:
            company_penalties_dict['car_callsign'] = ''
            company_penalties_dict['car_model'] = 'Нет данных'
            company_penalties_dict['car_number'] = ''
        company_penalties_dict['incident_date'] = penalty.incident_date
        company_penalties_dict['incident_speed'] = penalty.incident_speed
        company_penalties_dict['speed_recommend'] = penalty.speed_recommend
        company_penalties_dict['incident_place'] = penalty.incident_place
        company_penalties_dict['manager_comment'] = penalty.manager_comment
        company_penalties_dict['penalty_company'] = penalty.penalty_company
        company_penalties_dict['penalty_driver_paid_date'] = penalty.penalty_driver_paid_date
        company_penalties_dict['penalty_driver_paid'] = penalty.penalty_driver_paid
        company_penalties_chart.append(company_penalties_dict)

    # СТАТИСТИКА #
    # Компания
    company_penalties_open_count = company_penalties.exclude(id__in=driver_list_my_block).exclude(
        id__in=driver_list_sn_block).filter(penalty_driver_paid=False).count()
    company_penalties_open_sum = condition_or_0(
        company_penalties.exclude(id__in=driver_list_my_block).exclude(id__in=driver_list_sn_block).filter(
            penalty_driver_paid=False).aggregate(Sum('penalty_company'))['penalty_company__sum'])
    company_penalties_close_count = company_penalties.exclude(id__in=driver_list_my_block).exclude(
        id__in=driver_list_sn_block).filter(penalty_driver_paid=True).count()
    company_penalties_close_sum = condition_or_0(
        company_penalties.exclude(id__in=driver_list_my_block).exclude(id__in=driver_list_sn_block).filter(
            penalty_driver_paid=True).aggregate(Sum('penalty_company'))['penalty_company__sum'])
    company_penalties_total_count = company_penalties_open_count + company_penalties_close_count
    company_penalties_total_sum = company_penalties_open_sum + company_penalties_close_sum

    # ГИБДД
    gibdd_penalties_open_count = gibdd_penalties.exclude(id__in=driver_list_my_block).exclude(
        id__in=driver_list_sn_block).filter(penalty_driver_paid=False).count()
    gibdd_penalties_open_sum = condition_or_0(
        gibdd_penalties.filter(penalty_driver_paid=False).exclude(id__in=driver_list_my_block).exclude(
            id__in=driver_list_sn_block).aggregate(Sum('penalty_gibdd'))['penalty_gibdd__sum'])
    gibdd_penalties_close_count = gibdd_penalties.exclude(id__in=driver_list_my_block).exclude(
        id__in=driver_list_sn_block).filter(penalty_driver_paid=True).count()
    gibdd_penalties_close_sum = condition_or_0(
        gibdd_penalties.filter(penalty_driver_paid=True).exclude(id__in=driver_list_my_block).exclude(
            id__in=driver_list_sn_block).aggregate(Sum('penalty_gibdd'))['penalty_gibdd__sum'])
    gibdd_gibdd_close_count = gibdd_penalties.exclude(id__in=driver_list_my_block).exclude(
        id__in=driver_list_sn_block).filter(penalty_gibdd_paid=True).count()
    gibdd_gibdd_close_sum = condition_or_0(
        gibdd_penalties.filter(penalty_gibdd_paid=True).exclude(id__in=driver_list_my_block).exclude(
            id__in=driver_list_sn_block).aggregate(Sum('penalty_gibdd'))['penalty_gibdd__sum'])
    gibdd_gibdd_open_count = gibdd_penalties.exclude(id__in=driver_list_my_block).exclude(
        id__in=driver_list_sn_block).filter(penalty_gibdd_paid=False).count()
    gibdd_gibdd_open_sum = condition_or_0(
        gibdd_penalties.filter(penalty_gibdd_paid=False).exclude(id__in=driver_list_my_block).exclude(
            id__in=driver_list_sn_block).aggregate(Sum('penalty_gibdd'))['penalty_gibdd__sum'])

    gibdd_penalties_total_count = gibdd_penalties_close_count + gibdd_penalties_open_count
    gibdd_penalties_total_sum = gibdd_penalties_close_sum + gibdd_penalties_open_sum

    # КОНЕЦ СТАТИСТИКА #

    context = {'drivers_chart': sort_drivers_chart,
               'company_penalties_chart': company_penalties_chart,
               'gibdd_penalties_chart': gibdd_penalties_chart,
               'driver_id': in_driver_id,
               'company_penalties_open_count': company_penalties_open_count,
               'company_penalties_open_sum': company_penalties_open_sum,
               'company_penalties_close_count': company_penalties_close_count,
               'company_penalties_close_sum': company_penalties_close_sum,
               'company_penalties_total_count': company_penalties_total_count,
               'company_penalties_total_sum': company_penalties_total_sum,
               'gibdd_penalties_open_count': gibdd_penalties_open_count,
               'gibdd_penalties_open_sum': gibdd_penalties_open_sum,
               'gibdd_penalties_close_count': gibdd_penalties_close_count,
               'gibdd_penalties_close_sum': gibdd_penalties_close_sum,
               'gibdd_gibdd_close_count': gibdd_gibdd_close_count,
               'gibdd_gibdd_close_sum': gibdd_gibdd_close_sum,
               'gibdd_gibdd_open_count': gibdd_gibdd_open_count,
               'gibdd_gibdd_open_sum': gibdd_gibdd_open_sum,
               'gibdd_penalties_total_count': gibdd_penalties_total_count,
               'gibdd_penalties_total_sum': gibdd_penalties_total_sum,
               'stat_active': True}
    return render(request, 'gibdd_company_stat.html', context)


def find_incident_number(request, incident_number_in=None):
    car = Cars.objects.using('Cx_TaxiConfiguration')
    driver = Drivers.objects.using('Cx_TaxiConfiguration')

    try:
        incident = Gibdd.objects.get(incident_number=incident_number_in)
        incident.fullname = Drivers.objects.using('Cx_TaxiConfiguration').get(id=incident.driver_id).fullname
        incident.car_callsign = car.get(id=incident.car_id).callsign
        incident.car_model = car.get(id=incident.car_id).idmodel.name
        incident.car_number = car.get(id=incident.car_id).number
    except:
        incident = False

    context = {'incident_number_in': incident_number_in,
               'incident': incident}
    return render(request, 'find_incident_number.html', context)
