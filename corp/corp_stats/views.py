import calendar
import datetime

from django.contrib import auth
from django.db.models import Sum, Count
from django.http import Http404
from django.shortcuts import render, HttpResponseRedirect
from infinity.models import TsOrders, Corporations
from smena.models import Smena, Run
from salary.models import Payments


def login(request):
    if request.method == 'POST':
        print("POST data=", request.POST)
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


# ------ НАЧАЛО ОБЩИЕ ПЕРЕМЕННЫЕ И ФУНКЦИИ -----------

current_day = datetime.datetime.now()
# current_day = datetime.datetime(year=2017, month=3, day=2)
# Текущий МЕСЯЦ
first_day_of_current_month = current_day.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
sum_days_in_current_month = calendar.monthrange(first_day_of_current_month.year, first_day_of_current_month.month)[1]
last_day_of_current_month = current_day.replace(day=sum_days_in_current_month, hour=23, minute=59, second=59,
                                                microsecond=999)
end_current_day = current_day.replace(hour=23, minute=59, second=59, microsecond=999999)

# ПРОИЗВОЛЬНЫЙ МЕСЯЦ
first_day_of_month = current_day.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


# Число последнего дня месяца
def last_day_of_month(year, month):
    sum_days_in_month = calendar.monthrange(datetime.datetime(year=year, month=month, day=1).year,
                                            datetime.datetime(year=year, month=month, day=1).month)[1]
    return sum_days_in_month


def condition_or_0(condition):
    if condition:
        return int(condition)
    else:
        return 0


# Запрос всех заказов из базы статистики (все с State=7 -оплачен)
def get_orders(date_from, date_to, idcorporate=None):
    if idcorporate:
        orders = TsOrders.objects.using('Cx_TaxiStatistics').filter(deliverytime__range=(date_from, date_to),
                                                                    state=7).filter(idcorporate=idcorporate)
    else:
        orders = TsOrders.objects.using('Cx_TaxiStatistics').filter(deliverytime__range=(date_from, date_to),
                                                                    state=7)
    return orders


# собираем список id копративщиков, где есть ИНН для использования вхождения __in в запросе
corporate_list_id = [int(i['id']) for i in
                     Corporations.objects.using('Cx_TaxiConfiguration').filter(inn__isnull=False).values('id')]
# тоже самое без ИНН
corporate_list_id_no_inn = [int(i['id']) for i in
                            Corporations.objects.using('Cx_TaxiConfiguration').filter(inn__isnull=True).values('id')]


# ------ КОНЕЦ ОБЩИЕ ПЕРЕМЕННЫЕ И ФУНКЦИИ -----------


# ----- START ----- ВЫРУЧКА ПО ГОДАМ-МЕСЯЦАМ-ДНЯМ
def billing_y_m(request, in_year=current_day.year, in_month=current_day.month):
    # !!!! ЧАРТ С МЕСЯЦАМИ И ГОДАМИ !!!!
    current_day = datetime.datetime.now()
    date_chart = []
    for year in range(current_day.year, 2014, -1):
        for month in range(12, 0, -1):
            date_dict = dict()
            if year == current_day.year and month > current_day.month:
                continue
            if year == in_year and month == in_month:
                date_dict['current_month'] = True
            date_dict['year'] = year
            date_dict['month'] = datetime.datetime(year=year, month=month, day=1)
            orders_request = get_orders(datetime.datetime(year=year, month=month, day=1),
                                        datetime.datetime(year=year, month=month, day=last_day_of_month(year, month),
                                                          hour=23, minute=59, second=59, microsecond=999999))
            date_dict['all_money'] = condition_or_0(orders_request.aggregate(Sum('cost'))['cost__sum'])
            date_dict['all_orders'] = condition_or_0(orders_request.count())
            date_dict['all_money_cash'] = condition_or_0(
                orders_request.filter(isnotcash=0).filter(idcorporate__isnull=True).exclude(payedwithcard=1).aggregate(
                    Sum('cost'))['cost__sum'])
            date_dict['all_orders_cash'] = condition_or_0(
                orders_request.filter(isnotcash=0).filter(idcorporate__isnull=True).exclude(payedwithcard=1).count())
            date_dict['all_money_terminal'] = condition_or_0(
                orders_request.filter(isnotcash=0).filter(idcorporate__isnull=True).filter(payedwithcard=1).aggregate(
                    Sum('cost'))['cost__sum'])
            date_dict['all_orders_terminal'] = condition_or_0(
                orders_request.filter(isnotcash=0).filter(idcorporate__isnull=True).filter(
                    payedwithcard=1).count())
            date_dict['all_money_corp'] = condition_or_0(
                orders_request.filter(idcorporate__in=corporate_list_id).aggregate(Sum('cost'))['cost__sum'])
            date_dict['all_orders_corp'] = condition_or_0(
                orders_request.filter(idcorporate__in=corporate_list_id).count())
            date_dict['all_money_corp_no_inn'] = condition_or_0(
                orders_request.filter(idcorporate__in=corporate_list_id_no_inn).aggregate(Sum('cost'))['cost__sum'])
            date_dict['all_orders_corp_no_inn'] = condition_or_0(
                orders_request.filter(idcorporate__in=corporate_list_id_no_inn).count())
            date_dict['all_money_site_pay'] = condition_or_0(
                orders_request.filter(isnotcash=1).filter(idcorporate__isnull=True).aggregate(Sum('cost'))['cost__sum'])
            date_dict['all_orders_site_pay'] = condition_or_0(
                orders_request.filter(isnotcash=1).filter(idcorporate__isnull=True).count())
            date_chart.append(date_dict)
    # !!!! КОНЕЦ ЧАРТ С МЕСЯЦАМИ И ГОДАМИ !!!!

    # --- START --- Сумма значений по ГОДАМ
    year_chart = []
    for year in range(current_day.year, 2014, -1):
        result_dict = {}  # результирующий словарь
        for dictionary in date_chart:  # пробегаем по списку словарей
            for key in dictionary:  # пробегаем по ключам словаря
                if dictionary['year'] != year:
                    continue
                if key in ['current_month', 'year', 'month']:  # Убираем даты из словаря
                    continue
                dictionary[key] = int(dictionary[key])
                try:
                    result_dict[key] += dictionary[key]  # складываем значения
                except KeyError:  # если ключа еще нет - создаем
                    result_dict[key] = dictionary[key]
                dictionary[key] = '{0:,}'.format(dictionary[key]).replace(',', ' ')  # +Пробелы в числах для наглядности
        result_dict['year'] = year
        if year == current_day.year:
            result_dict['current_year'] = True
        year_chart.append(result_dict)

    # +Пробелы в числах для наглядности в year_chart (откл для Google graph)
    for dictionary in year_chart:
        for key in dictionary:
            if key == 'year':
                continue
            # dictionary[key] = '{0:,}'.format(dictionary[key]).replace(',', ' ')
    #  END Сумма значений по ГОДАМ

    billing_y_m_active = True
    context = {'billing_y_m_active': billing_y_m_active,
               'date_chart': date_chart,
               'year_chart': year_chart}
    return render(request, 'billing_y_m.html', context)


# ----- END ----- ВЫРУЧКА ПО ГОДАМ-МЕСЯЦАМ-ДНЯМ


# ----- START ----- ВЫРУЧКА ТЕКУЩИЙ МЕСЯЦ
def billing_current_m(request, in_month=current_day.month):
    # !!!! ЧАРТ ПО ДНЯМ !!!!
    current_day = datetime.datetime.now()
    date_chart = []
    for day in range(last_day_of_month(current_day.year, in_month), 0, -1):
        date_dict = dict()
        # if in_month != current_day.month:
        if day > current_day.day and in_month == current_day.month:
            continue
        if day == current_day.day and in_month == current_day.month:
            date_dict['current_day'] = True
        date_dict['day'] = datetime.datetime(year=current_day.year, month=in_month, day=day)
        orders_request = get_orders(datetime.datetime(year=current_day.year, month=in_month, day=day),
                                    datetime.datetime(year=current_day.year, month=in_month, day=day,
                                                      hour=23, minute=59, second=59, microsecond=999999))
        date_dict['all_money'] = condition_or_0(orders_request.aggregate(Sum('cost'))['cost__sum'])
        date_dict['all_orders'] = condition_or_0(orders_request.count())
        date_dict['all_money_cash'] = condition_or_0(
            orders_request.filter(isnotcash=0).filter(idcorporate__isnull=True).exclude(payedwithcard=1).aggregate(
                Sum('cost'))['cost__sum'])
        date_dict['all_orders_cash'] = condition_or_0(
            orders_request.filter(isnotcash=0).filter(idcorporate__isnull=True).exclude(payedwithcard=1).count())
        date_dict['all_money_terminal'] = condition_or_0(
            orders_request.filter(isnotcash=0).filter(idcorporate__isnull=True).filter(payedwithcard=1).aggregate(
                Sum('cost'))['cost__sum'])
        date_dict['all_orders_terminal'] = condition_or_0(
            orders_request.filter(isnotcash=0).filter(idcorporate__isnull=True).filter(
                payedwithcard=1).count())
        date_dict['all_money_corp'] = condition_or_0(
            orders_request.filter(idcorporate__in=corporate_list_id).aggregate(Sum('cost'))['cost__sum'])
        date_dict['all_orders_corp'] = condition_or_0(
            orders_request.filter(idcorporate__in=corporate_list_id).count())
        date_dict['all_money_corp_no_inn'] = condition_or_0(
            orders_request.filter(idcorporate__in=corporate_list_id_no_inn).aggregate(Sum('cost'))['cost__sum'])
        date_dict['all_orders_corp_no_inn'] = condition_or_0(
            orders_request.filter(idcorporate__in=corporate_list_id_no_inn).count())
        date_dict['all_money_site_pay'] = condition_or_0(
            orders_request.filter(isnotcash=1).filter(idcorporate__isnull=True).aggregate(Sum('cost'))['cost__sum'])
        date_dict['all_orders_site_pay'] = condition_or_0(
            orders_request.filter(isnotcash=1).filter(idcorporate__isnull=True).count())
        date_chart.append(date_dict)
    # !!!! КОНЕЦ ЧАРТ С МЕСЯЦАМИ И ГОДАМИ !!!!

    # --- START --- Сумма значений по МЕСЯЦАМ
    month_chart = []
    result_dict = {}  # результирующий словарь
    for dictionary in date_chart:  # пробегаем по списку словарей
        for key in dictionary:  # пробегаем по ключам словаря
            if key in ['day']:  # Убираем даты из словаря
                continue
            dictionary[key] = int(dictionary[key])
            try:
                result_dict[key] += dictionary[key]  # складываем значения
            except KeyError:  # если ключа еще нет - создаем
                result_dict[key] = dictionary[key]
    result_dict['month'] = datetime.datetime(year=current_day.year, month=in_month, day=1)
    result_dict['current_month'] = True
    month_chart.append(result_dict)

    # Список месяцев 12 шт
    month_list = []
    for month in range(1, 13, 1):
        if month > current_day.month:
            continue
        month_list.append(datetime.datetime(year=current_day.year, month=month, day=1))

    # +Пробелы в числах для наглядности в year_chart (откл для Google graph)
    # for dictionary in month_chart:
    #     for key in dictionary:
    #         if key == 'year':
    #             continue
    # dictionary[key] = '{0:,}'.format(dictionary[key]).replace(',', ' ')
    # --- END --- Сумма значений по МЕСЯЦАМ

    billing_current_m_active = True
    context = {'billing_current_m_active': billing_current_m_active,
               'date_chart': date_chart,
               'month_chart': month_chart,
               'month_list': month_list,
               'current_day': datetime.datetime(year=current_day.year, month=in_month, day=1)}
    return render(request, 'billing_current_m.html', context)


# ----- END ----- ВЫРУЧКА ТЕКУЩИЙ МЕСЯЦ


# ----- START ----- СМЕНА ПО ГОДАМ-МЕСЯЦАМ
def smena_y_m(request, in_year=current_day.year, in_month=current_day.month):
    # def get_smenas(date_from, date_to):
    #     smenas = Smena.objects.filter(date__range=(date_from, date_to))
    #     return smenas
    current_day = datetime.datetime.now()

    def get_year_smenas(year, month):
        smenas_year = Smena.objects.filter(date__range=(
            datetime.datetime(year=year, month=month, day=1, hour=0, minute=0, second=0, microsecond=0),
            datetime.datetime(year=year, month=month, day=last_day_of_month(year, month), hour=23, minute=59, second=59,
                              microsecond=999999)))
        return smenas_year

    def get_run_from_smenas(year, month):
        smena_list = [int(i['id']) for i in get_year_smenas(year, month).values('id')]
        run = Run.objects.filter(smena_id__in=smena_list).aggregate(Sum('run'))['run__sum']
        return run

    # !!!! ЧАРТ С ГОДАМИ + МЕСЯЦЫ  !!!!
    date_chart = []
    for year in range(current_day.year, 2017, -1):
        for month in range(12, 0, -1):
            date_dict = {}
            if year == current_day.year and month > current_day.month:
                continue
            if year == in_year and month == in_month:
                date_dict['current_month'] = True
            date_dict['year'] = year
            date_dict['month'] = datetime.datetime(year=year, month=month, day=1)
            date_dict['smenas_count'] = get_year_smenas(year, month).count()
            proceeds_cash = condition_or_0(
                get_year_smenas(year, month).aggregate(Sum('proceeds_cash'))['proceeds_cash__sum'])
            date_dict['proceeds_cash'] = proceeds_cash
            proceeds_terminal = condition_or_0(
                get_year_smenas(year, month).aggregate(Sum('proceeds_terminal'))['proceeds_terminal__sum'])
            date_dict['proceeds_terminal'] = proceeds_terminal
            proceeds_corporate_bank = condition_or_0(
                get_year_smenas(year, month).aggregate(Sum('proceeds_corporate_bank'))['proceeds_corporate_bank__sum'])
            date_dict['proceeds_corporate_bank'] = proceeds_corporate_bank
            all_money = condition_or_0(proceeds_cash + proceeds_terminal + proceeds_corporate_bank)
            date_dict['all_money'] = all_money
            money_to_boss_fact = condition_or_0(
                get_year_smenas(year, month).aggregate(Sum('money_to_boss_fact'))['money_to_boss_fact__sum'])
            date_dict['money_to_boss_fact'] = money_to_boss_fact
            delta_all_vs_boss = proceeds_cash - money_to_boss_fact
            date_dict['delta_all_vs_boss'] = delta_all_vs_boss
            date_dict['spending_fuel_cash'] = condition_or_0(
                get_year_smenas(year, month).aggregate(Sum('spending_fuel_cash'))['spending_fuel_cash__sum'])
            date_dict['spending_fuel_litres'] = condition_or_0(
                get_year_smenas(year, month).aggregate(Sum('spending_fuel_litres'))['spending_fuel_litres__sum'])
            date_dict['spending_carwash'] = condition_or_0(
                get_year_smenas(year, month).aggregate(Sum('spending_carwash'))['spending_carwash__sum'])
            date_dict['spending_carwash_bank'] = condition_or_0(
                get_year_smenas(year, month).aggregate(Sum('spending_carwash_bank'))['spending_carwash_bank__sum'])
            date_dict['spending_parking'] = condition_or_0(
                get_year_smenas(year, month).aggregate(Sum('spending_parking'))['spending_parking__sum'])
            date_dict['spending_washer'] = condition_or_0(
                get_year_smenas(year, month).aggregate(Sum('spending_washer'))['spending_washer__sum'])
            date_dict['spending_to'] = condition_or_0(
                get_year_smenas(year, month).aggregate(Sum('spending_to'))['spending_to__sum'])
            date_dict['spending_lamp'] = condition_or_0(
                get_year_smenas(year, month).aggregate(Sum('spending_lamp'))['spending_lamp__sum'])
            date_dict['spending_repair'] = condition_or_0(
                get_year_smenas(year, month).aggregate(Sum('spending_repair'))['spending_repair__sum'])
            date_dict['spending_etc'] = condition_or_0(
                get_year_smenas(year, month).aggregate(Sum('spending_etc'))['spending_etc__sum'])
            spending = condition_or_0(get_year_smenas(year, month).aggregate(Sum('spending'))['spending__sum'])
            date_dict['spending'] = spending
            date_dict['delta_delta_all_vs_boss_vs_spending'] = delta_all_vs_boss - spending
            # Подсчёт КМ
            km = condition_or_0(get_run_from_smenas(year, month))
            date_dict['km'] = km
            # /Подсчёт КМ
            # Смена с долгами водителя
            debt_chart = []
            for smena in get_year_smenas(year, month).filter(debt__gt=0):
                debt_dict = dict()
                debt_dict['id'] = smena.id
                debt_dict['date'] = smena.date
                debt_dict['debt'] = smena.debt
                debt_chart.append(debt_dict)
            # /Смена с долгами водителя
            date_dict['debt_chart'] = debt_chart
            date_chart.append(date_dict)
    # --- START --- Сумма значений по ГОДАМ
    year_chart = []
    for year in range(current_day.year, 2017, -1):
        result_dict = {}  # результирующий словарь
        for dictionary in date_chart:  # пробегаем по списку словарей
            for key in dictionary:  # пробегаем по ключам словаря
                if dictionary['year'] != year:
                    continue
                if key in ['current_month', 'year', 'month', 'debt_chart']:  # Убираем даты из словаря и др муть
                    continue
                dictionary[key] = int(dictionary[key])
                try:
                    result_dict[key] += dictionary[key]  # складываем значения
                except KeyError:  # если ключа еще нет - создаем
                    result_dict[key] = dictionary[key]
                dictionary[key] = '{0:,}'.format(dictionary[key]).replace(',', ' ')  # +Пробелы в числах для наглядности
        result_dict['year'] = year
        if year == current_day.year:
            result_dict['current_year'] = True
        year_chart.append(result_dict)

    # +Пробелы в числах для наглядности
    for dictionary in year_chart:
        for key in dictionary:
            if key == 'year':
                continue
            dictionary[key] = '{0:,}'.format(dictionary[key]).replace(',', ' ')
    #  END Сумма значений по ГОДАМ

    # !!!! КОНЕЦ ЧАРТ С ГОДАМИ + МЕСЯЦЫ !!!!
    smena_y_m_active = True
    context = {'date_chart': date_chart,
               'year_chart': year_chart,
               'smena_y_m_active': smena_y_m_active}
    return render(request, 'smena_y_m.html', context)


# ----- END ----- СМЕНА ПО ГОДАМ-МЕСЯЦАМ

# ----- START ----- ВЫРУЧКА ПО ГОДАМ-МЕСЯЦАМ
def profit(request, in_year=current_day.year, in_month=current_day.month):
    current_day = datetime.datetime.now()

    def get_year_smenas(year, month):
        smenas_year = Smena.objects.filter(date__range=(
            datetime.datetime(year=year, month=month, day=1, hour=0, minute=0, second=0, microsecond=0),
            datetime.datetime(year=year, month=month, day=last_day_of_month(year, month), hour=23, minute=59, second=59,
                              microsecond=999999)))
        return smenas_year

    def get_salary_payments(year, month):
        salary_payments = Payments.objects.filter(salary_id=int(str(year) + str(month)))
        return salary_payments

    # !!!! ЧАРТ С ГОДАМИ + МЕСЯЦЫ  !!!!
    date_chart = []
    for year in range(current_day.year, 2017, -1):
        for month in range(12, 0, -1):
            date_dict = {}
            if year == current_day.year and month > current_day.month:
                continue
            if year == in_year and month == in_month:
                date_dict['current_month'] = True
            date_dict['year'] = year
            date_dict['month'] = datetime.datetime(year=year, month=month, day=1)
            proceeds_cash = condition_or_0(
                get_year_smenas(year, month).aggregate(Sum('proceeds_cash'))['proceeds_cash__sum'])
            date_dict['proceeds_cash'] = proceeds_cash
            proceeds_terminal = condition_or_0(
                get_year_smenas(year, month).aggregate(Sum('proceeds_terminal'))['proceeds_terminal__sum'])
            date_dict['proceeds_terminal'] = proceeds_terminal
            proceeds_corporate_bank = condition_or_0(
                get_year_smenas(year, month).aggregate(Sum('proceeds_corporate_bank'))['proceeds_corporate_bank__sum'])
            date_dict['proceeds_corporate_bank'] = proceeds_corporate_bank
            all_money = condition_or_0(proceeds_cash + proceeds_terminal + proceeds_corporate_bank)
            date_dict['all_money'] = all_money
            date_dict['spending_fuel_cash'] = condition_or_0(
                get_year_smenas(year, month).aggregate(Sum('spending_fuel_cash'))['spending_fuel_cash__sum'])
            date_dict['spending_carwash'] = condition_or_0(
                get_year_smenas(year, month).aggregate(Sum('spending_carwash'))['spending_carwash__sum'])
            date_dict['spending_carwash_bank'] = condition_or_0(
                get_year_smenas(year, month).aggregate(Sum('spending_carwash_bank'))['spending_carwash_bank__sum'])
            date_dict['spending_parking'] = condition_or_0(
                get_year_smenas(year, month).aggregate(Sum('spending_parking'))['spending_parking__sum'])
            date_dict['spending_washer'] = condition_or_0(
                get_year_smenas(year, month).aggregate(Sum('spending_washer'))['spending_washer__sum'])
            date_dict['spending_to'] = condition_or_0(
                get_year_smenas(year, month).aggregate(Sum('spending_to'))['spending_to__sum'])
            date_dict['spending_lamp'] = condition_or_0(
                get_year_smenas(year, month).aggregate(Sum('spending_lamp'))['spending_lamp__sum'])
            date_dict['spending_repair'] = condition_or_0(
                get_year_smenas(year, month).aggregate(Sum('spending_repair'))['spending_repair__sum'])
            date_dict['spending_etc'] = condition_or_0(
                get_year_smenas(year, month).aggregate(Sum('spending_etc'))['spending_etc__sum'])
            spending = condition_or_0(get_year_smenas(year, month).aggregate(Sum('spending'))['spending__sum'])
            date_dict['spending'] = spending
            salary_payments = condition_or_0(get_salary_payments(year, month).aggregate(Sum('sum'))['sum__sum'])
            date_dict['salary_payments'] = salary_payments
            profit = all_money - spending - salary_payments
            date_dict['profit'] = profit
            date_chart.append(date_dict)
    # --- START --- Сумма значений по ГОДАМ
    year_chart = []
    for year in range(current_day.year, 2017, -1):
        result_dict = {}  # результирующий словарь
        for dictionary in date_chart:  # пробегаем по списку словарей
            for key in dictionary:  # пробегаем по ключам словаря
                if dictionary['year'] != year:
                    continue
                if key in ['current_month', 'year', 'month']:  # Убираем даты из словаря и др муть
                    continue
                dictionary[key] = int(dictionary[key])
                try:
                    result_dict[key] += dictionary[key]  # складываем значения
                except KeyError:  # если ключа еще нет - создаем
                    result_dict[key] = dictionary[key]
                dictionary[key] = '{0:,}'.format(dictionary[key]).replace(',', ' ')  # +Пробелы в числах для наглядности
        result_dict['year'] = year
        if year == current_day.year:
            result_dict['current_year'] = True
        year_chart.append(result_dict)

    # +Пробелы в числах для наглядности
    for dictionary in year_chart:
        for key in dictionary:
            if key == 'year':
                continue
            dictionary[key] = '{0:,}'.format(dictionary[key]).replace(',', ' ')
    #  END Сумма значений по ГОДАМ

    # !!!! КОНЕЦ ЧАРТ С ГОДАМИ + МЕСЯЦЫ !!!!
    profit_active = True
    context = {'date_chart': date_chart,
               'year_chart': year_chart,
               'profit_active': profit_active}
    return render(request, 'profit.html', context)


# ----- END ----- ВЫРУЧКА ПО ГОДАМ-МЕСЯЦАМ


# ----- START ----- КОРП КЛИЕНТЫ ПО ГОДАМ-МЕСЯЦАМ
def corp_y_m(request, in_year=current_day.year, in_month=current_day.month, in_corp_id=None):
    # список ИСКЛЮЧЕННЫХ корп. клиентов (просьба Иры от 13-03-2018: стойка+стойка бн)
    disable_corporate_list_id = [5007302971, 5007302950]
    disable_corp_list = []
    for id in disable_corporate_list_id:
        name = Corporations.objects.using('Cx_TaxiConfiguration').get(id=id).name
        disable_corp_list.append(name)

    # собираем список id копративщиков, где есть ИНН для использования вхождения __in в запросе
    corporate_list_id = [int(i['id']) for i in
                         Corporations.objects.using('Cx_TaxiConfiguration').filter(inn__isnull=False).exclude(
                             id__in=disable_corporate_list_id).values('id')]

    # !!!! ЧАРТ С МЕСЯЦАМИ И ГОДАМИ !!!!
    current_day = datetime.datetime.now()
    date_chart = []
    for year in range(current_day.year, 2015, -1):
        for month in range(12, 0, -1):
            date_dict = dict()
            if year == current_day.year and month > current_day.month:
                continue
            if year == in_year and month == in_month:
                date_dict['current_month'] = True
            date_dict['year'] = year
            date_dict['month'] = datetime.datetime(year=year, month=month, day=1)
            orders_request = get_orders(datetime.datetime(year=year, month=month, day=1),
                                        datetime.datetime(year=year, month=month, day=last_day_of_month(year, month),
                                                          hour=23, minute=59, second=59, microsecond=999999))
            all_corp_money_date_chart = condition_or_0(
                orders_request.filter(idcorporate__in=corporate_list_id).aggregate(Sum('cost'))['cost__sum'])
            date_dict['all_corp_money_date_chart'] = '{0:,}'.format(all_corp_money_date_chart).replace(',', ' ')
            all_corp_orders_date_chart = orders_request.filter(idcorporate__in=corporate_list_id).count()
            date_dict['all_corp_orders_date_chart'] = '{0:,}'.format(all_corp_orders_date_chart).replace(',', ' ')
            all_money_date_chart = condition_or_0(orders_request.aggregate(Sum('cost'))['cost__sum'])
            if all_corp_money_date_chart:
                date_dict['percent'] = all_corp_money_date_chart * 100 / all_money_date_chart
            else:
                date_dict['percent'] = 0
            date_chart.append(date_dict)
    # !!!! КОНЕЦ ЧАРТ С МЕСЯЦАМИ И ГОДАМИ !!!!

    # !!!! Чарт с корпоративным клиентами !!!!!
    final_corporate_chart = get_orders(datetime.datetime(year=in_year, month=in_month, day=1),
                                       datetime.datetime(year=in_year, month=in_month,
                                                         day=last_day_of_month(in_year, in_month), hour=23, minute=59,
                                                         second=59, microsecond=999999)).values('idcorporate').filter(
        idcorporate__isnull=False).exclude(idcorporate__in=disable_corporate_list_id).annotate(
        count=Count('idcorporate')).annotate(sum=Sum('cost')).order_by('-sum')
    # Добавляем к Корпоративным клиентам, с ИНН, их имена
    for corporate in final_corporate_chart:
        try:
            name = Corporations.objects.using('Cx_TaxiConfiguration').get(id=corporate['idcorporate']).name
            inn = Corporations.objects.using('Cx_TaxiConfiguration').get(id=corporate['idcorporate']).inn
            corporate['name'] = name
            if corporate['idcorporate'] == in_corp_id:
                corporate['current_corp'] = True
        except:
            corporate['name'] = None
        # Очищаем словарик из списка, где отсутствует ИНН у контрагента. Пока не знаю как удалить элемент из QuerrySet
        if inn:
            corporate['inn'] = inn
        else:
            corporate.clear()

    # Корпоратив с ИНН
    all_corp_money = condition_or_0(get_orders(datetime.datetime(year=in_year, month=in_month, day=1),
                                               datetime.datetime(year=in_year, month=in_month,
                                                                 day=last_day_of_month(in_year, in_month), hour=23,
                                                                 minute=59, second=59, microsecond=999999)).filter(
        idcorporate__in=corporate_list_id).aggregate(Sum('cost'))['cost__sum'])
    all_corp_money = '{0:,}'.format(all_corp_money).replace(',', ' ')
    all_corp_orders = get_orders(datetime.datetime(year=in_year, month=in_month, day=1),
                                 datetime.datetime(year=in_year, month=in_month,
                                                   day=last_day_of_month(in_year, in_month), hour=23, minute=59,
                                                   second=59, microsecond=999999)).filter(
        idcorporate__in=corporate_list_id).count()
    # !!!! КОНЕЦ Чарт с корпоративным клиентами !!!!!

    # !!!! ЧАРТ ЗАКАЗЫ КОРП КЛИЕНТА !!!!
    if in_corp_id:
        orders_current_corp = get_orders(datetime.datetime(year=in_year, month=in_month, day=1),
                                         datetime.datetime(year=in_year, month=in_month,
                                                           day=last_day_of_month(in_year, in_month), hour=23, minute=59,
                                                           second=59, microsecond=999999), in_corp_id).order_by(
            'deliverytime')
    else:
        orders_current_corp = None

    # !!!! КОНЕЦ ЧАРТ ЗАКАЗЫ КОРП КЛИЕНТА !!!!
    corp_y_m_active = True

    context = {'in_year': in_year,
               'in_month': in_month,
               'date_chart': date_chart,
               'final_corporate_chart': final_corporate_chart,
               'all_corp_money': all_corp_money,
               'all_corp_orders': all_corp_orders,
               'orders_current_corp': orders_current_corp,
               'corp_y_m_active': corp_y_m_active,
               'disable_corp_list': disable_corp_list
               }
    return render(request, 'corp_y_m.html', context)
# ----- END ----- КОРП КЛИЕНТЫ ПО ГОДАМ-МЕСЯЦАМ
