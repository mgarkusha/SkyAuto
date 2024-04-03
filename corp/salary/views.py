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
# Для таймера обновления временной табл
import time
import threading

from smena.models import Smena, Run
from complaints.models import Complaint
from gibdd.models import Gibdd, CompanyPenalty
from infinity.models import TsOrders, Drivers, Corporations
# from .forms import SmenaForm
from .models import Salary, Temporary, Payments
from .forms import PayslipForm, SalaryForm
from math import *


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


# Запрос всех значений из БД Salary_temp
def get_orders_from_temp():
    orders = Temporary.objects.all()
    return orders


# Запрос всех значений из БД Salary
def get_data_from_salary():
    data = Salary.objects.all()
    return data


# Список водителей, отключенных  от показа (Гаркуша, Федоров, Ушаков, Степанов)
driver_list_my_block = [5018737745, 5042082447, 5011597095, 5017290831]


# Список id работающих водителей из таблицы водителей (isblocked!=1, isdeleted!=1) за исключением driver_list_my_block
def driver_list_work_id():
    id = list([int(i['id']) for i in
               Drivers.objects.using('Cx_TaxiConfiguration').exclude(isblocked=1).exclude(isdeleted=1).exclude(
                   id__in=driver_list_my_block).values('id')])
    return id


# % от выручки 0.30 для всех, 0.25 для id_corp_discount_small
discount = 0.3
discount_small = 0.25
# Список id корп.клиентов (стойка и стойка б/н), для которых discount=0.25
id_corp_discount_small = [5007302971, 5007302950]
# Коэффициент за низкий расход, РУБ
fuel_rate = 35


# Считаем ЗП. base - из какой базы считаем, discount - скидка
def get_salary_for_driver(base, driver_id, discount, corp_list_id=None):
    if corp_list_id:
        salary_sum = condition_or_0(base.filter(iddriver=driver_id).filter(
            idcorporate__in=corp_list_id).aggregate(Sum('cost'))['cost__sum']) * discount
    else:
        salary_sum = condition_or_0(base.filter(iddriver=driver_id).exclude(
            idcorporate__in=id_corp_discount_small).aggregate(Sum('cost'))['cost__sum']) * discount
    return ceil(salary_sum)


# НАЧАЛО Считаем расход топлива по формуле Иры от 12-02-2018 "Миша, для ЗП посчитай так: Весь пробег / 10 - Все литры"
def calculate_fuel(date_from, date_to, driver_id):
    all_fuel_current_month = \
        Smena.objects.filter(date__range=(date_from, date_to)).filter(
            driver_id=driver_id).aggregate(Sum('spending_fuel_litres'))['spending_fuel_litres__sum']
    smena_list_id = list([int(i['id']) for i in Smena.objects.filter(driver_id=driver_id).filter(
        date__range=(date_from, date_to)).values('id')])
    all_km_current_month = Run.objects.filter(smena_id__in=smena_list_id).aggregate(Sum('run'))['run__sum']

    def calc_fuel(km, fuel):
        if km and fuel:
            calc = km / 10 - fuel
            fuel_out = float("%.1f" % calc)
        else:
            fuel_out = '0'
        return fuel_out

    return calc_fuel(all_km_current_month, all_fuel_current_month)


def calculate_fuel_bonus(fuel):
    fuel = float(fuel)
    if fuel:
        if fuel <= 0:
            fuel_bonus = 0
        else:
            fuel_bonus = fuel * fuel_rate
    else:
        fuel_bonus = 0
    return ceil(fuel_bonus)


# КОНЕЦ Считаем расход топлива по формуле Иры от 12-02-2018


# !!!!!!!!!!!!!!! Стартовая страница ЗП /salary !!!!!!!!!!!!!!
def salary(request):
    # Список водителей, отключенных  от показа (1.Гаркуша)
    driver_list_my_block_names = []
    for id in driver_list_my_block:
        name = Drivers.objects.using('Cx_TaxiConfiguration').get(id=id).fullname
        driver_list_my_block_names.append(name)
    # Если наступил след. мес, а временная табл. не от этого месяца, то обновляем
    temp_order = Temporary.objects.all().values('deliverytime')[:1]
    try:
        if temp_order[0]['deliverytime'].month != first_day_of_current_month.month:
            salary_refresh(request)
    except:
        salary_refresh(request)

    # Собираем список id водителей, которые работали за период+фильтр что не заблокированы
    # Множество(set), чтобы убрать повторения id
    driver_work_list_id = set(
        list([int(i['iddriver']) for i in
              get_orders_from_temp().filter(iddriver__in=driver_list_work_id()).values('iddriver')]))
    # Список и кол-во id водителей, которым осталось досформировать ЗП за прошлый мес
    driver_list_id_salary_last_month = list([int(i['driver_id']) for i in
                                             Salary.objects.filter(salary_year=first_day_last_month.year,
                                                                   salary_month=first_day_last_month.month).values(
                                                 'driver_id')])
    driver_list_id_without_salary = set(list([int(i['iddriver']) for i in
                                              get_orders_range(first_day_last_month, last_day_last_month).exclude(
                                                  iddriver__in=driver_list_id_salary_last_month).filter(
                                                  iddriver__in=driver_list_work_id()).values('iddriver')]))
    driver_list_id_without_salary_count = len(driver_list_id_without_salary)
    # Маркер о недосформированной ЗП за прошлый мес
    if driver_list_id_without_salary and current_day().day >= 2:
        marker_salary_last_month = True
    else:
        marker_salary_last_month = False

    drvier_chart = []
    salary_fund_current_month = 0
    for driver_id in driver_list_work_id():
        salary_chart = []
        driver_dict = dict()
        driver_dict['driver_id'] = driver_id
        driver_name = Drivers.objects.using('Cx_TaxiConfiguration').get(id=driver_id).fullname
        driver_dict['fullname'] = driver_name.split()
        driver_dict['fullname_small'] = driver_name.split()[:2]
        # Маркер ДИСПЕТЧЕРА
        if driver_dict['fullname'][0] == 'яя':
            driver_dict['operator_marker'] = True
            driver_dict['fullname'] = driver_name.split()[:3]
            driver_dict['fullname_small'] = driver_name.split()[:3]
        driver_dict['first_day_of_month'] = first_day_of_current_month
        driver_dict['last_day_of_month'] = last_day_of_current_month
        # Маркер АВАНСА за тек. месяц
        if Salary.objects.filter(driver_id=driver_id).filter(salary_year=first_day_of_current_month.year,
                                                             salary_month=first_day_of_current_month.month):
            driver_dict['salary_marker'] = True
            avans_marker = True
        else:
            avans_marker = False
        if Salary.objects.filter(salary_year=first_day_of_current_month.year,
                                 salary_month=first_day_of_current_month.month):
            marker_salary_current_month = True
        else:
            marker_salary_current_month = False
        # Конец - Маркер АВАНСА за тек. месяц
        # START --- Вывод аванса в drvier_chart, если он был
        try:
            driver_sal = \
                Salary.objects.filter(driver_id=driver_id).filter(
                    salary_month=first_day_of_current_month.month).order_by(
                    '-date')[0]
            pay_sum = \
                Payments.objects.filter(salary_id=driver_sal.salary_id).filter(driver_id=driver_id).aggregate(
                    Sum('sum'))[
                    'sum__sum']
            driver_dict['pay_sum'] = format_number(condition_or_0(pay_sum))
        except:
            driver_dict['pay_sum'] = 0
        # END --- Вывод аванса в drvier_chart, если он был
        salary_sum = condition_or_0(get_salary_for_driver(get_orders_from_temp(), driver_id, discount))
        driver_dict['salary_sum'] = format_number(salary_sum)
        salary_sum_stoyka = condition_or_0(
            get_salary_for_driver(get_orders_from_temp(), driver_id, discount_small, id_corp_discount_small))
        driver_dict['salary_sum_stoyka'] = format_number(salary_sum_stoyka)
        # Средний расход топлива за смены за текущий месяц + бонус
        driver_dict['fuel'] = calculate_fuel(first_day_of_current_month, last_day_of_current_month, driver_id)
        fuel_bonus = condition_or_0(calculate_fuel_bonus(driver_dict['fuel']))
        driver_dict['fuel_bonus'] = format_number(fuel_bonus)
        # КОНЕЦ Средний расход топлива за смены за текущий месяц + бонус
        salary_total = salary_sum + salary_sum_stoyka + fuel_bonus
        driver_dict['salary_total'] = format_number(condition_or_0(salary_total))
        salary_fund_current_month += salary_total
        try:
            if avans_marker:
                last_salarys = Salary.objects.filter(driver_id=driver_id).order_by('-date')[:3]
            else:
                last_salarys = Salary.objects.filter(driver_id=driver_id).order_by('-date')[:2]
            for sal in last_salarys:
                salary_dict = dict()
                # salary_dict['date'] = sal.date
                salary_dict['driver_id'] = driver_id
                salary_dict['salary_id'] = sal.salary_id
                salary_dict['salary_date'] = datetime.datetime(year=sal.salary_year, month=sal.salary_month,
                                                               day=1)
                salary_dict['workdays'] = sal.workdays
                salary_dict['payment'] = sal.payment
                salary_dict['salary_sum'] = format_number(sal.salary_nal_term_corp)
                salary_dict['salary_sum_stoyka'] = format_number(condition_or_0(sal.salary_airport))
                salary_total = condition_or_0(sal.salary_total) + condition_or_0(sal.salary_add) + condition_or_0(
                    sal.fuel_bonus)
                salary_dict['salary_total'] = format_number(salary_total)
                salary_dict['fuel_bonus'] = condition_or_0(sal.fuel_bonus)
                salary_dict['salary_add'] = condition_or_0(sal.salary_add)
                salary_dict['salary_add_comment'] = sal.salary_add_comment
                pay_sum = condition_or_0(
                    Payments.objects.filter(salary_id=sal.salary_id).filter(driver_id=sal.driver_id).aggregate(
                        Sum('sum'))['sum__sum'])
                salary_dict['pay_sum'] = format_number(condition_or_0(pay_sum))
                debt_sum = salary_total - condition_or_0(
                    Payments.objects.filter(salary_id=sal.salary_id).filter(driver_id=sal.driver_id).aggregate(
                        Sum('sum'))['sum__sum']) - condition_or_0(sal.deduction)
                salary_dict['debt_sum'] = format_number(condition_or_0(debt_sum))
                salary_chart.append(salary_dict)
            driver_dict['salary_chart'] = salary_chart
        except:
            driver_dict['last_salary'] = 'Нет данных'
        drvier_chart.append(driver_dict)
    salary_fund_current_month = format_number(salary_fund_current_month)

    # Сортируем по fullname
    sort_fullname_chart = []
    for i in sorted(drvier_chart, key=operator.itemgetter("fullname")):
        sort_fullname_chart.append(i)

    # ФОНДЫ ЗП + ВЫПЛ / НЕ ВЫПЛ (в шапке левой таблицы)
    salary = Salary.objects.all()
    # last_salarys = Salary.objects.

    # -начало- Для корректной сортировки ФОНДА ЗП
    # list_id_salary - список id ЗП, cut - срез
    # Возвращается отсортированный список ID ЗП
    def sort_fund(list_id_salary, cut):
        salary_list_id_new = list()
        for i in list_id_salary:
            if len(str(i)) < 6:
                i *= 10
                lst = list(str(i))
                lst[-1], lst[-2] = lst[-2], lst[-1]
                i = int(''.join(lst))
            salary_list_id_new.append(i)
        salary_list_id_new = sorted(salary_list_id_new, reverse=True)[:cut]
        salary_list_id_old = list()
        for i in salary_list_id_new:
            if list(str(i))[-2] == '0':
                lst = list(str(i))
                lst[-2], lst[-1] = lst[-1], ''
                i = int(''.join(lst))
            salary_list_id_old.append(i)
        return salary_list_id_old
    # -конец- Для корректной сортировки ФОНДА ЗП

    # Список уникальных id зп ведомостей (set - множ.для уникальности, reversed - обратная сортировка)
    salary_list_id = set(list([int(i['salary_id']) for i in salary.values('salary_id')]))
    if marker_salary_current_month:
        salary_list_id = sort_fund(salary_list_id, 3)
    else:
        salary_list_id = sort_fund(salary_list_id, 2)

    fund_chart = []
    for salary_id in salary_list_id:
        fund_dict = dict()
        current_salary = salary.filter(salary_id=salary_id)
        fund_dict['date'] = datetime.datetime(year=current_salary[0].salary_year, month=current_salary[0].salary_month,
                                              day=1)
        fund_dict['fuel_bonus'] = condition_or_0(current_salary.aggregate(Sum('fuel_bonus'))['fuel_bonus__sum'])
        fund_dict['salary_add'] = condition_or_0(current_salary.aggregate(Sum('salary_add'))['salary_add__sum'])
        salary_fund = current_salary.aggregate(Sum('salary_total'))['salary_total__sum'] + fund_dict['fuel_bonus'] + \
                      fund_dict['salary_add']
        fund_dict['salary_fund'] = format_number(condition_or_0(salary_fund))
        salary_paid_out = condition_or_0(Payments.objects.filter(salary_id=salary_id).aggregate(Sum('sum'))['sum__sum'])
        fund_dict['salary_paid_out'] = format_number(condition_or_0(salary_paid_out))
        salary_unpaid = salary_fund - salary_paid_out
        fund_dict['salary_unpaid'] = format_number(condition_or_0(salary_unpaid))
        fund_dict['salary_nal_term_corp'] = condition_or_0(
            current_salary.aggregate(Sum('salary_nal_term_corp'))['salary_nal_term_corp__sum'])
        fund_dict['salary_airport'] = condition_or_0(
            current_salary.aggregate(Sum('salary_airport'))['salary_airport__sum'])
        fund_chart.append(fund_dict)
    # КОНЕЦ ФОНДЫ ЗП + ВЫПЛ / НЕ ВЫПЛ

    context = {'current_day': current_day(),
               'name_last_month': last_month,
               'salary_fund_current_month': salary_fund_current_month,
               'driver_chart': sort_fullname_chart,
               'marker_salary_current_month': marker_salary_current_month,
               'marker_salary_last_month': marker_salary_last_month,
               'driver_list_id_without_salary_count': driver_list_id_without_salary_count,
               'fuel_rate': fuel_rate,
               'discount': discount,
               'discount_small': discount_small,
               'driver_list_my_block_names': driver_list_my_block_names,
               'fund_chart': fund_chart}
    return render(request, 'salary.html', context)


# START --- Документы выплаты ЗП --- PAYSLIP
def payslip(request, driver_id, salary_id):
    salary = Salary.objects.get(salary_id=salary_id, driver_id=driver_id)
    # START --- Если ЗП текущего месяца, то UPDATE таблицы salary_salary перед открытием
    if salary.salary_year == first_day_of_current_month.year and salary.salary_month == first_day_of_current_month.month:
        salary.salary_nal_term_corp = get_salary_for_driver(
            get_orders_range(first_day_of_current_month, last_day_of_current_month), driver_id, discount)
        salary.salary_airport = get_salary_for_driver(
            get_orders_range(first_day_of_current_month, last_day_of_current_month), driver_id, discount_small,
            id_corp_discount_small)
        salary.fuel = calculate_fuel(first_day_of_current_month, last_day_of_current_month, driver_id)
        salary.fuel_bonus = calculate_fuel_bonus(salary.fuel)
        salary.salary_total = salary.salary_nal_term_corp + salary.salary_airport
        salary.save()
    # END --- Если ЗП текущего месяца, то UPDATE таблицы salary_salary перед открытием
    # --- СТАРТ --- Апдейт штрафов. Жалобы - дата рассмотрения/закрытия штрафа, гибдд/компания - дате документа
    salary.deduction = condition_or_0(Complaint.objects.filter(complaint_date_close__year=salary.salary_year,
                                                               complaint_date_close__month=salary.salary_month).filter(
        driver_id=driver_id).aggregate(Sum('complaint_penalty'))['complaint_penalty__sum']) + condition_or_0(
        Gibdd.objects.filter(date__year=salary.salary_year, date__month=salary.salary_month).filter(
            driver_id=driver_id).aggregate(Sum('penalty_gibdd'))['penalty_gibdd__sum']) + condition_or_0(
        CompanyPenalty.objects.filter(date__year=salary.salary_year, date__month=salary.salary_month).filter(
            driver_id=driver_id).aggregate(Sum('penalty_company'))['penalty_company__sum'])
    salary.save()
    # --- ФИНИШ ---
    smenas = Smena.objects.filter(driver_id=driver_id).filter(date__month=salary.salary_month).filter(
        date__year=salary.salary_year)
    payments = Payments.objects.filter(driver_id=driver_id).filter(salary_id=salary_id)
    # smenas_list_id = list([int(i['id']) for i in smenas.values('id')])
    if request.method == 'POST':
        payslip_form = PayslipForm(request.POST)
        salary_form = SalaryForm(request.POST, instance=salary)
        if payslip_form.is_valid():
            post = payslip_form.save(commit=False)
            salary_post = salary_form.save(commit=False)
            post.date = datetime.date.today()
            post.salary_id = salary_id
            post.driver_id = driver_id
            post.sum = condition_or_0(request.POST.get('sum'))
            # Если сумма выплаты 0, то скорее всего сделали "Доначислено"
            if salary_post.salary_add != request.POST.get('salary_add'):
                if salary_form.is_valid():
                    salary_post.salary_add = condition_or_0(request.POST.get('salary_add'))
                    salary_post.salary_add_comment = request.POST.get('salary_add_comment')
                    salary_post.save()
            if salary_post.fuel_bonus != request.POST.get('fuel_bonus'):
                if salary_form.is_valid():
                    salary_post.fuel_bonus = condition_or_0(request.POST.get('fuel_bonus'))
                    salary_post.save()
            # Если в форме ЗП выплачена, то закрываем ЗП
            if request.POST.get('is_payment') and salary.payment is False:
                if salary_form.is_valid():
                    salary_post.payment = True
                    salary_post.save()
                    # Если закрываем ЗП, то Штрафы ГИБДД и КОМПАНИИ, выкатанные за этот месяц, делаем оплаченными
                    gibdd_chart = Gibdd.objects.filter(date__year=salary.salary_year,
                                                       date__month=salary.salary_month).filter(
                        driver_id=driver_id)
                    for i in gibdd_chart:
                        i.penalty_driver_paid = True
                        i.save()
                    company_penalty_chart = CompanyPenalty.objects.filter(date__year=salary.salary_year,
                                                                          date__month=salary.salary_month).filter(
                        driver_id=driver_id)
                    for i in company_penalty_chart:
                        i.penalty_driver_paid = True
                        i.save()
            # Если в форме ЗП добавили долг за предприятием, то открываем ЗП
            elif not request.POST.get('is_payment') and salary.payment is True:
                if salary_form.is_valid():
                    salary_post.payment = False
                    salary_post.save()
                    # Если открываем ЗП, то Штрафы ГИБДД и КОМПАНИИ, выкатанные за этот месяц, делаем не оплаченными
                    # Так придумала Ира (хз почему)
                    gibdd_chart = Gibdd.objects.filter(date__year=salary.salary_year,
                                                       date__month=salary.salary_month).filter(
                        driver_id=driver_id)
                    for i in gibdd_chart:
                        i.penalty_driver_paid = False
                        i.save()
                    company_penalty_chart = CompanyPenalty.objects.filter(date__year=salary.salary_year,
                                                                          date__month=salary.salary_month).filter(
                        driver_id=driver_id)
                    for i in company_penalty_chart:
                        i.penalty_driver_paid = False
                        i.save()
            if post.sum == 0:
                return HttpResponseRedirect('/salary')
            post.sum_comment = request.POST.get('sum_comment')
            post.save()
        # return HttpResponseRedirect('/salary')
        return HttpResponseRedirect('/salary/%d/%d/' % (driver_id, salary_id))
    else:
        # --- ШАПКА ---
        driver_fullname = Drivers.objects.using('Cx_TaxiConfiguration').get(id=driver_id).fullname
        salary_date = datetime.datetime(year=salary.salary_year, month=salary.salary_month, day=1)
        # --- СТАРТ --- Начислено
        # -- Если ЗП есть в БД Salary --
        # - Заказы -
        salary_nal_term_corp = condition_or_0(salary.salary_nal_term_corp)
        salary_airport = condition_or_0(salary.salary_airport)
        salary_all_and_airport = condition_or_0(salary_nal_term_corp + salary_airport)
        # - Бензин -
        smenas_chart = []
        smenas_run_result = 0
        spending_fuel_litres_result = 0
        for smena in smenas:
            smena_dict = dict()
            smena_dict['date'] = smena.date
            smena_dict['run'] = condition_or_0(Run.objects.filter(smena_id=smena.id).aggregate(Sum('run'))['run__sum'])
            smena_dict['spending_fuel_litres'] = smena.spending_fuel_litres
            smenas_chart.append(smena_dict)
            smenas_run_result += smena_dict['run']
            spending_fuel_litres_result += smena_dict['spending_fuel_litres']
        fuel_bonus = ceil(salary.fuel_bonus)
        # - Доначислено -
        salary_add = condition_or_0(salary.salary_add)
        salary_add_comment = salary.salary_add_comment
        # Если ЗП нет в БД Salary, то создаём
        accrued_result = salary_all_and_airport + fuel_bonus + salary_add
        # --- СТАРТ --- ДЕНЬГИ НА РУКАХ
        try:
            last_smena = Smena.objects.filter(driver_id=driver_id).order_by('-date')[0]
            cash_on_hands = format_number(condition_or_0(TsOrders.objects.using('Cx_TaxiStatistics').filter(
                deliverytime__range=(last_smena.finish_date + second_plus_one,
                                     current_day().replace(hour=23, minute=59, second=59,
                                                           microsecond=999999)), state=7).filter(
                iddriver=driver_id).filter(isnotcash=0).exclude(payedwithcard=1).aggregate(Sum('cost'))['cost__sum']))
        except:
            cash_on_hands = 0
        # --- ФИНИШ --- ДЕНЬГИ НА РУКАХ
        # --- ФИНИШ --- Начислено

        # --- СТАРТ --- Удержано
        # -старт- Жалобы
        complaints = Complaint.objects.filter(complaint_date_close__year=salary.salary_year,
                                              complaint_date_close__month=salary.salary_month).filter(
            driver_id=driver_id)
        # Если сумма штрафа 0, то это выговор
        complaints_penalty_chart = complaints.filter(complaint_penalty__gt=0)
        complaints_penalty_result = condition_or_0(
            complaints.aggregate(Sum('complaint_penalty'))['complaint_penalty__sum'])
        complaints_rebuke = 0
        for i in complaints:
            if i.complaint_penalty == 0:
                complaints_rebuke += 1
        # -финиш- Жалобы
        # -старт- ГИБДД
        gibdd_chart = Gibdd.objects.filter(date__year=salary.salary_year, date__month=salary.salary_month).filter(
            driver_id=driver_id)
        gibdd_penalty_result = condition_or_0(gibdd_chart.aggregate(Sum('penalty_gibdd'))['penalty_gibdd__sum'])
        # company_penalty_result = condition_or_0(gibdd_chart.aggregate(Sum('penalty_company'))['penalty_company__sum'])
        # -финиш- ГИБДД
        # -старт- ШТРАФ КОМПАНИИ
        company_penalty_chart = CompanyPenalty.objects.filter(date__year=salary.salary_year,
                                                              date__month=salary.salary_month).filter(
            driver_id=driver_id)
        company_penalty_result = condition_or_0(
            company_penalty_chart.aggregate(Sum('penalty_company'))['penalty_company__sum'])
        # -финиш- ШТРАФ КОМПАНИИ
        hold_result = complaints_penalty_result + gibdd_penalty_result + company_penalty_result
        # --- ФИНИШ --- Удержано

        # --- СТАРТ --- Выплачено
        payment_result = 0
        payment_chart = []
        for payment in payments:
            payment_dict = dict()
            payment_dict['payment_id'] = payment.id
            payment_dict['date'] = payment.date
            payment_dict['sum_comment'] = payment.sum_comment
            payment_dict['sum'] = payment.sum
            payment_chart.append(payment_dict)
            payment_result += condition_or_0(payment.sum)
        # --- ФИНИШ --- Выплачено
        # Долг за предприятием и окончательный расчёт
        debt_sum = accrued_result - payment_result
        is_payment = salary.payment
        # --- СТАРТ ---
        # --- ФИНИШ ---
        context = {'driver_id': driver_id,
                   'salary_id': salary_id,
                   'driver_fullname': driver_fullname,
                   'salary_date': salary_date,
                   # Начислено
                   'salary_nal_term_corp': salary_nal_term_corp,
                   'salary_airport': salary_airport,
                   'salary_all_and_airport': salary_all_and_airport,
                   'smenas_chart': smenas_chart,
                   'smenas_run_result': smenas_run_result,
                   'spending_fuel_litres_result': spending_fuel_litres_result,
                   'fuel_rate': fuel_rate,
                   'fuel_bonus': fuel_bonus,
                   'salary_add': salary_add,
                   'salary_add_comment': salary_add_comment,
                   # Удержано
                   'complaints_penalty_chart': complaints_penalty_chart,
                   'complaints_penalty_result': complaints_penalty_result,
                   'complaints_rebuke': complaints_rebuke,
                   'gibdd_chart': gibdd_chart,
                   'gibdd_penalty_result': gibdd_penalty_result,
                   'company_penalty_chart': company_penalty_chart,
                   'company_penalty_result': company_penalty_result,
                   'hold_result': hold_result,
                   # Выплаты
                   'payment_chart': payment_chart,
                   # Итоги
                   'cash_on_hands': cash_on_hands,
                   'payment_result': payment_result,
                   'accrued_result': accrued_result,
                   'debt_sum': debt_sum,
                   'is_payment': is_payment}
    return render(request, 'payslip_cu.html', context)


# Удаление выплаты
def payment_d(request, payment_id, driver_id, salary_id):
    payment = get_object_or_404(Payments, id=payment_id)
    payment.delete()
    return HttpResponseRedirect('/salary/%d/%d/' % (driver_id, salary_id))


# FINISH --- Документы выплаты ЗП --- PAYSLIP

# Собираем временную таблицу с заказами за текущий месяц, предварительно её очистив. Кнопка REFRESH в Salary.html
def salary_refresh(request):
    temp = Temporary.objects.all()
    temp.delete()
    for order in get_orders_range(first_day_of_current_month, last_day_of_current_month):
        temp = Temporary.objects.create(deliverytime=order.deliverytime, iddriver=order.iddriver,
                                        idcorporate=order.idcorporate, cost=order.cost)
        temp.save()
    return HttpResponseRedirect('/salary')


# START --- АВАНС ВОДИТЕЛЮ  ---
def salary_driver_create(request, driver_id):
    salary_id = float(str(first_day_of_current_month.year) + str(first_day_of_current_month.month))
    salary_nal_term_corp = get_salary_for_driver(
        get_orders_range(first_day_of_current_month, last_day_of_current_month), driver_id, discount)
    salary_airport = get_salary_for_driver(get_orders_range(first_day_of_current_month, last_day_of_current_month),
                                           driver_id, discount_small, id_corp_discount_small)
    fuel = calculate_fuel(first_day_of_current_month, last_day_of_current_month, driver_id)
    fuel_bonus = calculate_fuel_bonus(fuel)
    salary_total = salary_nal_term_corp + salary_airport

    salary = Salary.objects.create(salary_id=salary_id, driver_id=driver_id,
                                   salary_year=first_day_of_current_month.year,
                                   salary_month=first_day_of_current_month.month, workdays=0, payment=False,
                                   salary_total=salary_total, salary_nal_term_corp=salary_nal_term_corp,
                                   salary_airport=salary_airport, fuel=fuel, fuel_bonus=fuel_bonus, salary_add=0,
                                   salary_add_comment='')
    salary.save()
    return HttpResponseRedirect('/salary/%d/%d/' % (driver_id, salary_id))


# FINISH --- АВАНС ВОДИТЕЛЮ ---


#  Сформировать ЗП за прошлый месяц
def salary_create(request):
    # Проверяем, сформирована ли ЗП по водителю. Чтобы избежать дубля ЗП по месяцу. И искл из driver_list_id
    driver_list_id_salary_last_month = list([int(i['driver_id']) for i in
                                             Salary.objects.filter(salary_year=first_day_last_month.year,
                                                                   salary_month=first_day_last_month.month).values(
                                                 'driver_id')])
    # Собираем список id водителей, которые работали за период+фильтр что не заблокированы
    # Множество(set), чтобы убрать повторения id
    driver_list_id = set(list([int(i['iddriver']) for i in
                               get_orders_range(first_day_last_month, last_day_last_month).exclude(
                                   iddriver__in=driver_list_id_salary_last_month).filter(
                                   iddriver__in=driver_list_work_id()).values('iddriver')]))
    # ФОРМИРУЕМ ЗП у кого небыло ни АВАНСА ни ЗП
    for driver_id in driver_list_id:
        salary_id = float(str(first_day_last_month.year) + str(first_day_last_month.month))
        salary_nal_term_corp = \
            get_salary_for_driver(get_orders_range(first_day_last_month, last_day_last_month), driver_id, discount)
        salary_airport = \
            get_salary_for_driver(get_orders_range(first_day_last_month, last_day_last_month), driver_id,
                                  discount_small,
                                  id_corp_discount_small)
        fuel = calculate_fuel(first_day_last_month, last_day_last_month, driver_id)
        fuel_bonus = calculate_fuel_bonus(fuel)
        deduction = condition_or_0(Complaint.objects.filter(complaint_date_close__year=first_day_last_month.year,
                                                            complaint_date_close__month=first_day_last_month.month).filter(
            driver_id=driver_id).aggregate(Sum('complaint_penalty'))['complaint_penalty__sum'])

        salary_total = salary_nal_term_corp + salary_airport

        salary = Salary.objects.create(salary_id=salary_id, driver_id=driver_id, salary_year=first_day_last_month.year,
                                       salary_month=first_day_last_month.month, workdays=0, payment=False,
                                       salary_total=salary_total, salary_nal_term_corp=salary_nal_term_corp,
                                       salary_airport=salary_airport, fuel=fuel, fuel_bonus=fuel_bonus, salary_add=0,
                                       salary_add_comment='', deduction=deduction)
        salary.save()
    # АПДЕЙТИМ ЗП у кого был АВАНС
    for id in driver_list_id_salary_last_month:
        salary = Salary.objects.get(driver_id=id, salary_year=first_day_last_month.year,
                                    salary_month=first_day_last_month.month)
        salary.salary_nal_term_corp = get_salary_for_driver(
            get_orders_range(first_day_last_month, last_day_last_month), id, discount)
        salary.salary_airport = get_salary_for_driver(
            get_orders_range(first_day_last_month, last_day_last_month), id, discount_small,
            id_corp_discount_small)
        salary.fuel = calculate_fuel(first_day_last_month, last_day_last_month, id)
        salary.fuel_bonus = calculate_fuel_bonus(salary.fuel)
        salary.salary_total = salary.salary_nal_term_corp + salary.salary_airport
        salary.deduction = condition_or_0(Complaint.objects.filter(complaint_date_close__year=first_day_last_month.year,
                                                                   complaint_date_close__month=first_day_last_month.month).filter(
            driver_id=id).aggregate(Sum('complaint_penalty'))['complaint_penalty__sum']) + condition_or_0(
            Gibdd.objects.filter(date__year=salary.salary_year, date__month=salary.salary_month).filter(
                driver_id=driver_id).aggregate(Sum('penalty_gibdd'))['penalty_gibdd__sum']) + condition_or_0(
            CompanyPenalty.objects.filter(date__year=salary.salary_year, date__month=salary.salary_month).filter(
                driver_id=driver_id).aggregate(Sum('penalty_company'))['penalty_company__sum'])
        salary.save()
    # Обновляем временную таблицу
    salary_refresh(request)
    return HttpResponseRedirect('/salary')
