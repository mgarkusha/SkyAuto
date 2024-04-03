from django.shortcuts import render, render_to_response, get_object_or_404, HttpResponseRedirect
from django.db.models import Sum, Count, Min, Max
from .models import Cars, Carmodels, Drivers, TsOrders, Corporations, TaOrders, Parkings, Clientcontacts
from ats.models import FSms
from datetime import datetime, timedelta
# from django.utils import timezone
from django.contrib import auth
from django.http import Http404
import calendar
import datetime
import psycopg2
import operator


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


# ----------- ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ И ФУНКЦИИ ------------------------ #
one_second = timedelta(seconds=1)


def condition_or_0(condition):
    if condition:
        return condition
    else:
        return 0


# /----------- ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ И ФУНКЦИИ ------------------------ #


def chart(request):
    # Для бага с самопроизвольным изменением ИНН корп клиента в ИНФИНИТИ
    corporate_inn_bug = False
    # Определяемся с датами-временем для запросов
    test_day = datetime.datetime.now()
    # current_day со всякими приколами
    # current_day = test_day.replace(year=2017, month=11, day=19, hour=10, minute=0, second=0)
    # current_day тестовый
    # current_day = test_day.replace(year=2017, month=11, day=10, hour=12, minute=0, second=0)
    current_day = datetime.datetime.now()

    day_plus_one = timedelta(days=1)
    start_current_day = current_day.replace(hour=0, minute=0, second=0, microsecond=0)
    start_day_parade = current_day.replace(hour=0, minute=0, second=0, microsecond=0) - day_plus_one
    end_current_day = current_day.replace(hour=23, minute=59, second=59, microsecond=999999)
    previous_day = start_current_day - one_second
    start_previous_day = previous_day.replace(hour=0, minute=0, second=0, microsecond=0)
    end_previous_day = previous_day.replace(hour=23, minute=59, second=59, microsecond=999999)
    start_next_day = current_day + day_plus_one
    start_next_day = start_next_day.replace(hour=0, minute=0, second=0, microsecond=0)
    end_next_day = start_next_day.replace(hour=23, minute=59, second=59, microsecond=999999)

    lastMonth = datetime.date.today().replace(day=1) - datetime.timedelta(days=1)

    # Считаем кол-во машин ONLINE
    cars_online = Cars.objects.using('Cx_TaxiConfiguration').exclude(state=1).count()
    # Считаем кол-во машин ЗАПЛАНИРОВАННЫХ НА ЗАКАЗ
    cars_online_on_plan = Cars.objects.using('Cx_TaxiConfiguration').filter(state=7).count()
    # Считаем кол-во машин НА ЗАКАЗЕ + ЗАПЛАНИРОВАННЫЕ
    cars_online_on_orders = Cars.objects.using('Cx_TaxiConfiguration').filter(state=3).count() + cars_online_on_plan
    # Считаем кол-во машин НА ПЕРЕРЫВЕ
    cars_online_pause = Cars.objects.using('Cx_TaxiConfiguration').filter(state=4).count()
    # Считаем кол-во машин СВОБОДНЫЕ
    cars_online_free = cars_online - cars_online_on_orders - cars_online_pause

    # собираем список id копративщиков, где есть ИНН для использования вхождения __in в запросе
    corporate_list_id = [int(i['id']) for i in
                         Corporations.objects.using('Cx_TaxiConfiguration').filter(inn__isnull=False).values('id')]
    # тоже самое без ИНН
    corporate_list_id_no_inn = [int(i['id']) for i in
                                Corporations.objects.using('Cx_TaxiConfiguration').filter(inn__isnull=True).values(
                                    'id')]

    # Запрос всех предварительные заказв (все с State=1 -предварительные + State=14 - Горящие)
    def get_plan_orders(start, end):
        orders_plan_today = TaOrders.objects.using('Cx_TaxiActive').filter(
            deliverytime__range=(start, end), state__in=[1, 14])
        return orders_plan_today

    # Запрос всех активных в данный момент заказов (все кроме State=1(предварительные) и 14(горящие))
    def get_active_orders():
        orders_active_now = TaOrders.objects.using('Cx_TaxiActive').filter(
            deliverytime__range=(start_current_day, end_current_day)).exclude(state__in=[1, 14])
        return orders_active_now

    # Запрос всех заказов из базы статистики (все с State=7 -оплачен)
    def get_orders(start_date, end_date):
        orders_current_day = TsOrders.objects.using('Cx_TaxiStatistics').filter(
            deliverytime__range=(start_date, end_date), state=7)
        return orders_current_day

    #
    # ------------ ВОДИТЕЛИ -----------
    #
    # Хит-парад водителей. Основной запрос.
    final_driver_chart = get_orders(start_current_day, end_current_day).values('iddriver').annotate(
        countt=Count('iddriver')).annotate(
        summ=Sum('cost')).annotate(firs_order=Min('starttime')).annotate(last_order=Max('finishtime')).order_by(
        'summ')
    # Хит-парад водителей. Старт: минус 2 дня.
    final_parade_chart = get_orders(start_day_parade, end_current_day).values('iddriver').annotate(
        countt=Count('iddriver')).annotate(
        summ=Sum('cost')).annotate(firs_order=Min('starttime')).annotate(last_order=Max('finishtime')).order_by(
        'summ')

    # Хит-парад водителя за текущий день.
    def current_driver_chart(iddriver):
        return get_orders(start_current_day, end_current_day).filter(iddriver=iddriver).values('iddriver').annotate(
            countt=Count('iddriver')).annotate(summ=Sum('cost'))

    # Хит-парад водителя за прошлый день.
    def current_driver_chart_prev_day(iddriver):
        return get_orders(start_previous_day, end_previous_day).filter(iddriver=iddriver).values('iddriver').annotate(
            countt=Count('iddriver')).annotate(summ=Sum('cost'))

    # Добавляем к таблице с водителями авто, которые на линии, но водители которых не выполнили ни одного заказа
    # то есть исключаем всех тех, кто ксть в final_driver_chart и Cx_TaxiActive(где есть iddriver)
    driver_id_list_statistics_base = [driver['iddriver'] for driver in final_driver_chart]
    orders_active_now = TaOrders.objects.using('Cx_TaxiActive').values('iddriver').filter(
        deliverytime__range=(start_current_day, end_current_day)).exclude(idcar__isnull=True)

    driver_id_list_active_base = [driver['iddriver'] for driver in orders_active_now]
    # Водители, которые онлайн. Но их нет в статистике сегодня и нет в активных заказах сейчас
    cars_online_list_without_stat_and_without_active = Cars.objects.using('Cx_TaxiConfiguration').exclude(
        idcurrentdriver__id__in=driver_id_list_statistics_base).exclude(
        idcurrentdriver__id__in=list(filter(None, driver_id_list_active_base))).exclude(state=1).exclude(
        state=3).exclude(state=7)
    # Водители, которые онлайн. Но их нет в статистике сегодня, но уже полуили первый заказ (активные заказы)
    cars_online_list_without_stat_and_in_active = Cars.objects.using('Cx_TaxiConfiguration').exclude(
        idcurrentdriver__id__in=driver_id_list_statistics_base).filter(
        idcurrentdriver__id__in=driver_id_list_active_base).exclude(state=1)
    for driver in cars_online_list_without_stat_and_in_active:
        order = TaOrders.objects.using('Cx_TaxiActive').filter(iddriver=driver.idcurrentdriver.id)
        driver.cost = order[0].cost
        driver.starttime = order[0].starttime
        driver.destination_zone_name = order[0].destinationzonestr

    # Текущие парковки. Кол-во машин на них.
    # parking_count = Cars.objects.using('Cx_TaxiConfiguration').values('idparking').annotate(
    #     countt=Count('idparking'))
    # print(parking_count)

    for driver in final_parade_chart:
        try:
            name = Drivers.objects.using('Cx_TaxiConfiguration').get(id=driver['iddriver']).fullname
        except:
            name = 'Без имени'
        driver['fullname'] = name
        # Из в какую зону едет
        cars = Cars.objects.using('Cx_TaxiConfiguration').filter(idcurrentdriver=driver['iddriver'])
        if cars:
            driver['car'] = cars[0]
            driver['carmodel'] = cars[0].idmodel.name
            driver['online_status'] = 'on'
            if cars[0].idparking:
                driver['parking_name'] = cars[0].idparking.name
            try:
                driver['destination_zone_name'] = TaOrders.objects.using('Cx_TaxiActive').get(
                    iddriver=driver['iddriver']).destinationzonestr
            except:
                driver['destination_zone_name'] = ''
            # Сумма,руб заказов за текущий день
            # print(driver['iddriver'], current_driver_chart(driver['iddriver']), current_driver_chart_prev_day(driver['iddriver']))
            try:
                driver['summ_today'] = current_driver_chart(driver['iddriver'])[0]['summ']
                driver['countt_today'] = current_driver_chart(driver['iddriver'])[0]['countt']
            except:
                driver['summ_today'] = 0
                driver['countt_today'] = 0

            try:
                driver['summ_previous_day'] = current_driver_chart_prev_day(driver['iddriver'])[0]['summ']
            except:
                driver['summ_previous_day'] = 0

            # Прибавляем к конечной сумме, сумму из активного заказа и ставим маркер
            try:
                order = TaOrders.objects.using('Cx_TaxiActive').filter(iddriver=driver['iddriver'])
                driver['summ_plus'] = order[0].cost
                driver['summ_total'] = driver['summ'] + order[0].cost
                # driver['summ_active'] = True
                driver['summ_today_total'] = driver['summ_today'] + order[0].cost
            except:
                driver['summ_active'] = False
                driver['summ_total'] = driver['summ']
                driver['summ_today_total'] = driver['summ_today']
        else:
            driver['car'] = None
            driver['carmodel'] = None
            driver['parking_name'] = ''
            driver['online_status'] = 'off'

    #
    # ----------   КОРПОРАТИВНЫЕ КЛИЕНТЫ   -------------
    #
    # Чарт с корпоративным клиентами
    final_corporate_chart = get_orders(start_current_day, end_current_day).values('idcorporate').filter(
        idcorporate__isnull=False).annotate(
        count=Count('idcorporate')).annotate(sum=Sum('cost')).order_by('-sum')
    # Чарт с корп. клиентами для тех кто будет без инн
    final_corporate_chart_no_inn = get_orders(start_current_day, end_current_day).values('idcorporate').filter(
        idcorporate__isnull=False).annotate(
        count=Count('idcorporate')).annotate(sum=Sum('cost')).order_by('-sum')
    # Добавляем к Корпоративным клиентам, с ИНН, их имена
    for corporate in final_corporate_chart:
        try:
            corp = Corporations.objects.using('Cx_TaxiConfiguration').get(id=corporate['idcorporate'])
            corporate['name'] = corp.name
            # START Активные заказы сейчас + Запланированные на сегодня
            # - Предварительные
            try:
                corp_pre = TaOrders.objects.using('Cx_TaxiActive').filter(
                    deliverytime__range=(start_current_day, end_current_day), state__in=[1, 14]).filter(
                    idcorporate=corporate['idcorporate']).order_by('-deliverytime')
                corporate['pre_count'] = corp_pre.count()
                corporate['pre_sum'] = corp_pre.aggregate(Sum('cost'))['cost__sum']
            except:
                corporate['pre_count'] = None
                corporate['pre_sum'] = None
            # - Активные
            try:
                corp_active = TaOrders.objects.using('Cx_TaxiActive').filter(
                    deliverytime__range=(start_current_day, end_current_day), state__in=[3, 4, 5, 7, 11]).filter(
                    idcorporate=corporate['idcorporate']).order_by('-deliverytime')
                corporate['active_count'] = corp_active.count()
                corporate['active_sum'] = corp_active.aggregate(Sum('cost'))['cost__sum']
            except:
                corporate['active_count'] = None
                corporate['active_sum'] = None
            # FINISH Активные заказы сейчас + Запланированные на сегодня
            if corp.inn:
                corporate['inn'] = corp.inn
            else:
                # Очищаем словарик из списка, где отсутствует ИНН у контрагента. Пока не знаю как удалить элемент из QuerrySet
                corporate.clear()
        except:
            corporate.clear()
            corporate_inn_bug = True
    for corporate in final_corporate_chart_no_inn:
        try:
            corp = Corporations.objects.using('Cx_TaxiConfiguration').get(id=corporate['idcorporate'])
            corporate['name'] = corp.name
            if corp.inn:
                # Очищаем словарик из списка, где отсутствует ИНН у контрагента. Пока не знаю как удалить элемент из QuerrySet
                corporate.clear()
            else:
                corporate['inn'] = corp.inn
        except:
            corporate.clear()
            corporate_inn_bug = True
    # Выявление баганутых заказов с непонятными ID корп клиентов
    corporations_list_id = list(
        [int(i['id']) for i in Corporations.objects.using('Cx_TaxiConfiguration').values('id')])
    corporate_orders_bug_list = get_orders(start_current_day, end_current_day).filter(
        idcorporate__isnull=False).exclude(
        idcorporate__in=corporations_list_id)

    # Заказы, корп.клиентов с ИНН, но почему-то оплаченные не по безналу.
    corporate_orders_with_inn_but_cash_pay = get_orders(start_current_day, end_current_day).filter(
        idcorporate__in=corporate_list_id).filter(isnotcash=0)
    # Добавляем к Корпоративным клиентам, их имена
    for corporate in corporate_orders_with_inn_but_cash_pay:
        name = Corporations.objects.using('Cx_TaxiConfiguration').get(id=corporate.idcorporate).name
        corporate.name = name

    #
    # --------------- АНАЛИТИКА Cx_TaxiStatistics ----------------
    #
    # ТУТ НЕМНОГО НЕКРАСИВО, НАДО БЫ КОГДА НИБУДЬ ПЕРЕДЕЛАТЬ!!! =)
    # --------------- Выполненные СЕГОДНЯ по категориям ---------------
    all_money_current_day = condition_or_0(
        get_orders(start_current_day, end_current_day).aggregate(Sum('cost'))['cost__sum'])
    all_orders_current_day = get_orders(start_current_day, end_current_day).count()
    # нал
    all_money_cash = condition_or_0(
        get_orders(start_current_day, end_current_day).filter(isnotcash=0).filter(idcorporate__isnull=True).exclude(
            payedwithcard=1).aggregate(
            Sum('cost'))['cost__sum'])
    all_orders_cash = get_orders(start_current_day, end_current_day).filter(isnotcash=0).filter(
        idcorporate__isnull=True).exclude(payedwithcard=1).count()
    # терминал
    all_money_terminal = condition_or_0(
        get_orders(start_current_day, end_current_day).filter(isnotcash=0).filter(idcorporate__isnull=True).filter(
            payedwithcard=1).aggregate(
            Sum('cost'))['cost__sum'])
    all_orders_terminal = get_orders(start_current_day, end_current_day).filter(isnotcash=0).filter(
        idcorporate__isnull=True).filter(
        payedwithcard=1).count()
    # сайт
    all_money_site_pay = condition_or_0(
        get_orders(start_current_day, end_current_day).filter(isnotcash=1).filter(idcorporate__isnull=True).aggregate(
            Sum('cost'))['cost__sum'])
    all_orders_site_pay = get_orders(start_current_day, end_current_day).filter(isnotcash=1).filter(
        idcorporate__isnull=True).count()
    # Корпоратив с ИНН
    all_corp_money_current_day = condition_or_0(
        get_orders(start_current_day, end_current_day).filter(idcorporate__in=corporate_list_id).aggregate(Sum('cost'))[
            'cost__sum'])
    all_corp_orders_current_day = get_orders(start_current_day, end_current_day).filter(
        idcorporate__in=corporate_list_id).count()
    # Корпоратив без ИНН
    all_corp_money_current_day_no_inn = condition_or_0(
        get_orders(start_current_day, end_current_day).filter(idcorporate__in=corporate_list_id_no_inn).aggregate(
            Sum('cost'))['cost__sum'])
    all_corp_orders_current_day_no_inn = get_orders(start_current_day, end_current_day).filter(
        idcorporate__in=corporate_list_id_no_inn).count()

    # --------------- Выполненные ВЧЕРА по категориям ---------------
    all_money_previous_day = condition_or_0(
        get_orders(start_previous_day, end_previous_day).aggregate(Sum('cost'))['cost__sum'])
    all_orders_previous_day = get_orders(start_previous_day, end_previous_day).count()
    # нал
    all_money_cash_previous_day = condition_or_0(
        get_orders(start_previous_day, end_previous_day).filter(isnotcash=0).filter(idcorporate__isnull=True).exclude(
            payedwithcard=1).aggregate(
            Sum('cost'))['cost__sum'])
    all_orders_cash_previous_day = get_orders(start_previous_day, end_previous_day).filter(isnotcash=0).filter(
        idcorporate__isnull=True).exclude(payedwithcard=1).count()
    # терминал
    all_money_terminal_previous_day = condition_or_0(
        get_orders(start_previous_day, end_previous_day).filter(isnotcash=0).filter(idcorporate__isnull=True).filter(
            payedwithcard=1).aggregate(
            Sum('cost'))['cost__sum'])
    all_orders_terminal_previous_day = get_orders(start_previous_day, end_previous_day).filter(isnotcash=0).filter(
        idcorporate__isnull=True).filter(
        payedwithcard=1).count()
    # сайт
    all_money_site_pay_previous_day = condition_or_0(
        get_orders(start_previous_day, end_previous_day).filter(isnotcash=1).filter(idcorporate__isnull=True).aggregate(
            Sum('cost'))['cost__sum'])
    all_orders_site_pay_previous_day = get_orders(start_previous_day, end_previous_day).filter(isnotcash=1).filter(
        idcorporate__isnull=True).count()
    # Корпоратив с ИНН
    all_corp_money_previous_day = condition_or_0(
        get_orders(start_previous_day, end_previous_day).filter(idcorporate__in=corporate_list_id).aggregate(
            Sum('cost'))[
            'cost__sum'])
    all_corp_orders_previous_day = get_orders(start_previous_day, end_previous_day).filter(
        idcorporate__in=corporate_list_id).count()
    # Корпоратив без ИНН
    all_corp_money_previous_day_no_inn = condition_or_0(
        get_orders(start_previous_day, end_previous_day).filter(idcorporate__in=corporate_list_id_no_inn).aggregate(
            Sum('cost'))['cost__sum'])
    all_corp_orders_previous_day_no_inn = get_orders(start_previous_day, end_previous_day).filter(
        idcorporate__in=corporate_list_id_no_inn).count()

    # Планирование заказов
    # plan_rub = 200000
    # plan_order = 200
    # percent_rub = int(all_money_current_day) * 100 // plan_rub  # Процент от плана, руб
    # percent_order = int(all_orders_current_day) * 100 // plan_order  # Процент от плана, заказы
    # sum_remaind_rub = plan_rub - int(all_money_current_day)
    # sum_remaind_order = plan_order - int(all_orders_current_day)
    # /АНАЛИТИКА Cx_TaxiStatistics

    # АНАЛИТИКА Cx_TaxiActive
    # предварительные на сегодня и завтра по интервалам
    pre_intervals = [{'start_h': 0, 'finish_h': 2, 'finish_ms': 59},
                     {'start_h': 3, 'finish_h': 3, 'finish_ms': 59},
                     {'start_h': 4, 'finish_h': 4, 'finish_ms': 59},
                     {'start_h': 5, 'finish_h': 5, 'finish_ms': 59},
                     {'start_h': 6, 'finish_h': 6, 'finish_ms': 59},
                     {'start_h': 7, 'finish_h': 7, 'finish_ms': 59},
                     {'start_h': 8, 'finish_h': 8, 'finish_ms': 59},
                     {'start_h': 9, 'finish_h': 12, 'finish_ms': 59},
                     {'start_h': 13, 'finish_h': 16, 'finish_ms': 59},
                     {'start_h': 17, 'finish_h': 20, 'finish_ms': 59},
                     {'start_h': 21, 'finish_h': 23, 'finish_ms': 59}]

    for i in pre_intervals:
        money_today = get_plan_orders(start_current_day.replace(hour=i['start_h']),
                                      end_current_day.replace(hour=i['finish_h'], minute=i['finish_ms'],
                                                              second=i['finish_ms'])).aggregate(Sum('cost'))[
            'cost__sum']
        orders_today = get_plan_orders(start_current_day.replace(hour=i['start_h']),
                                       end_current_day.replace(hour=i['finish_h'], minute=i['finish_ms'],
                                                               second=i['finish_ms'])).count()
        money_nextday = get_plan_orders(start_next_day.replace(hour=i['start_h']),
                                        end_next_day.replace(hour=i['finish_h'], minute=i['finish_ms'],
                                                             second=i['finish_ms'])).aggregate(Sum('cost'))[
            'cost__sum']
        orders_nextday = get_plan_orders(start_next_day.replace(hour=i['start_h']),
                                         end_next_day.replace(hour=i['finish_h'], minute=i['finish_ms'],
                                                              second=i['finish_ms'])).count()
        i['money_today'] = money_today
        i['orders_today'] = orders_today
        i['money_nextday'] = money_nextday
        i['orders_nextday'] = orders_nextday
        i['finish_h'] = i['finish_h'] + 1

    # предварительные на сегодня. сумма и кол-во
    pre_money_current_day = get_plan_orders(start_current_day, end_current_day).aggregate(Sum('cost'))['cost__sum'] if \
        get_plan_orders(start_current_day, end_current_day).aggregate(Sum('cost'))['cost__sum'] else 0
    pre_orders_current_day = get_plan_orders(start_current_day, end_current_day).count()
    # предварительные на завтра. сумма и кол-во
    pre_money_next_day = get_plan_orders(start_next_day, end_next_day).aggregate(Sum('cost'))['cost__sum'] if \
        get_plan_orders(start_next_day, end_next_day).aggregate(Sum('cost'))['cost__sum'] else 0
    pre_orders_next_day = get_plan_orders(start_next_day, end_next_day).count()
    now_money_current_day = get_active_orders().aggregate(Sum('cost'))['cost__sum'] if \
        get_active_orders().aggregate(Sum('cost'))['cost__sum'] else 0
    now_orders_current_day = get_active_orders().count()
    # /АНАЛИТИКА Cx_TaxiActive

    # АНАЛИТИКА Планируется на конец дня
    plan_money_current_day = all_money_current_day + pre_money_current_day + now_money_current_day
    plan_orders_current_day = all_orders_current_day + pre_orders_current_day + now_orders_current_day
    # /АНАЛИТИКА Планируется на конец дня

    # --- START --- Поздравлялка с 8 марта :)
    if current_day.day == 8 and current_day.month == 3:
        grats_8_march = True
    else:
        grats_8_march = False
    # --- END --- Поздравлялка с 8 марта :)

    # -- start -- НОВЫЕ КЛИЕНТЫ ЗА ТЕКУЩИЕ: ДЕНЬ / МЕСЯЦ / МЕСЯЦ ПУЛКОВО
    conn = psycopg2.connect(
        "dbname='Cx_TaxiStatistics' user='cxdbuser' host='127.0.0.1' password='cxdbwizard' port='10000'")
    cur = conn.cursor()
    cur.execute("""
select sum(cnt_day) cnt_day, sum(cnt_month) cnt_month, sum(cnt_month_airport) cnt_month_airport
from (
  select count(*) cnt_day, 0 cnt_month, 0 cnt_month_airport
  from "TS_Orders"
  where date("DeliveryTime") = current_date 
  and "Phone" not in (
    select "Phone" as phone
    from "TS_Orders" ts_o
    where "DeliveryTime" between '2013-01-01' and current_date - 1
    and "Phone" is not null and "Phone" not in ('', 'с руки')
    )
  union all
  select 0, count(*), 0
  from "TS_Orders"
  where EXTRACT(month from "DeliveryTime") = EXTRACT(month from current_date) and EXTRACT(year from "DeliveryTime") = EXTRACT(year from current_date)
  and "Phone" not in (
    select "Phone" as phone
    from "TS_Orders" ts_o
    where "DeliveryTime" between '2013-01-01' and date_trunc('month',now()) - '0 day 00:00:01'::interval
    and "Phone" is not null and "Phone" not in ('', 'с руки'))
  union all
  select 0, 0, count(*)
  from "TS_Orders"
  where EXTRACT(month from "DeliveryTime") = EXTRACT(month from current_date) and EXTRACT(year from "DeliveryTime") = EXTRACT(year from current_date)
  and "IDDeliveryAddress" = '5087572348'
  and "Phone" not in (
    select "Phone" as phone
    from "TS_Orders" ts_o
    where "DeliveryTime" between '2013-01-01' and date_trunc('month',now()) - '0 day 00:00:01'::interval
    and "Phone" is not null and "Phone" not in ('', 'с руки'))
) tt
    """)
    rows = cur.fetchall()
    today_new_clients = 0
    last_month_new_clients = 0
    last_month_new_clients_pulkovo = 0
    for row in rows:
        today_new_clients = row[0]
        last_month_new_clients = row[1]
        last_month_new_clients_pulkovo = row[2]

    # --- end --- НОВЫЕ КЛИЕНТЫ ЗА ТЕКУЩИЕ: ДЕНЬ / МЕСЯЦ / МЕСЯЦ ПУЛКОВО

    # --- start --- SMS CHART
    def serial_date_to_string(srl_no):
        new_date = datetime.datetime(1900, 1, 1, 0, 0) + datetime.timedelta(srl_no - 2)
        return new_date.strftime("%d.%m.%Y")

    def sms_state(state):
        msg = ''
        if state == 1:
            msg = 'Отправлено'
        elif state == 2:
            msg = 'Доставлено'
        elif state == 3:
            msg = 'Ошибка'
        elif state == 0:
            msg = 'В очереди'
        return msg

    def sms_errorcode(errorcode):
        msg = ''
        if errorcode == -1004:
            msg = 'Абонент недоступен'
        elif errorcode == -1007:
            msg = 'Вышел срок доставки'
        elif errorcode == -1008:
            msg = 'Ошибка маршрутизации'
        elif errorcode == 1:
            msg = 'Ошибка шлюза'
        return msg

    start_day = datetime.datetime(year=1899, month=12, day=30)
    current_day_in_days = str(current_day - start_day).split()[0]
    sms_querry = FSms.objects.using('fb').filter(datetime_d=current_day_in_days).all().order_by('datetime_t')

    def client_name_querry(phone):
        try:
            client_name = Clientcontacts.objects.using('Cx_TaxiConfiguration').get(
                contact__contains=phone).idabonent
        except:
            client_name = ''
        return client_name

    sms_chart = []
    for i in sms_querry:
        sms_dict = dict()
        sms_dict['datetime_d'] = serial_date_to_string(i.datetime_d)
        sms_dict['datetime_t'] = (datetime.datetime.min + datetime.timedelta(seconds=86400 * i.datetime_t)).time()
        sms_dict['number'] = i.number
        sms_dict['client_name'] = client_name_querry(i.number)
        sms_dict['partscount'] = i.partscount
        sms_dict['textsms'] = i.textsms
        sms_dict['state'] = sms_state(i.state)
        sms_dict['sms_state'] = i.state
        sms_dict['errorcode'] = sms_errorcode(i.errorcode)
        sms_chart.append(sms_dict)
    sms_chart.reverse()
    # --- end --- SMS CHART

    context = {'current_day': current_day,
               'all_corp_money_current_day': all_corp_money_current_day,
               'all_corp_orders_current_day': all_corp_orders_current_day,
               'all_corp_money_current_day_no_inn': all_corp_money_current_day_no_inn,
               'all_corp_orders_current_day_no_inn': all_corp_orders_current_day_no_inn,
               'corporate_orders_with_inn_but_cash_pay': corporate_orders_with_inn_but_cash_pay,
               'all_money_current_day': all_money_current_day, 'all_orders_current_day': all_orders_current_day,
               'all_money_cash': all_money_cash, 'all_orders_cash': all_orders_cash,
               'all_money_terminal': all_money_terminal, 'all_orders_terminal': all_orders_terminal,
               'all_money_corp_no_inn': all_corp_money_current_day_no_inn,
               'all_orders_corp_no_inn': all_corp_orders_current_day_no_inn,
               'all_money_corp': all_corp_money_current_day, 'all_orders_corp': all_corp_orders_current_day,
               'all_money_site_pay': all_money_site_pay, 'all_orders_site_pay': all_orders_site_pay,
               # Статистика за ВЧЕРА
               'previous_day': previous_day,
               'all_money_previous_day': all_money_previous_day,
               'all_orders_previous_day': all_orders_previous_day,
               'all_money_cash_previous_day': all_money_cash_previous_day,
               'all_orders_cash_previous_day': all_orders_cash_previous_day,
               'all_money_terminal_previous_day': all_money_terminal_previous_day,
               'all_orders_terminal_previous_day': all_orders_terminal_previous_day,
               'all_money_site_pay_previous_day': all_money_site_pay_previous_day,
               'all_orders_site_pay_previous_day': all_orders_site_pay_previous_day,
               'all_corp_money_previous_day': all_corp_money_previous_day,
               'all_corp_orders_previous_day': all_corp_orders_previous_day,
               'all_corp_money_previous_day_no_inn': all_corp_money_previous_day_no_inn,
               'all_corp_orders_previous_day_no_inn': all_corp_orders_previous_day_no_inn,
               # /Статистика за ВЧЕРА
               'plan_money_current_day': plan_money_current_day, 'plan_orders_current_day': plan_orders_current_day,
               'pre_intervals': pre_intervals,
               'pre_money_current_day': pre_money_current_day, 'pre_orders_current_day': pre_orders_current_day,
               'pre_money_next_day': pre_money_next_day, 'pre_orders_next_day': pre_orders_next_day,
               'now_money_current_day': now_money_current_day, 'now_orders_current_day': now_orders_current_day,
               'cars_online': cars_online,
               'cars_online_on_orders': cars_online_on_orders,
               'cars_online_pause': cars_online_pause,
               'cars_online_free': cars_online_free,
               'final_driver_chart': final_parade_chart,
               'final_driver_offline_chart': final_driver_chart,
               'cars_online_list_without_stat_and_without_active': cars_online_list_without_stat_and_without_active,
               'cars_online_list_without_stat_and_in_active': cars_online_list_without_stat_and_in_active,
               'final_corporate_chart': final_corporate_chart,
               'final_corporate_chart_no_inn': final_corporate_chart_no_inn,
               'grats_8_march': grats_8_march,
               'corporate_inn_bug': corporate_inn_bug,
               'corporate_orders_bug_list': corporate_orders_bug_list,
               # Новые клиенты
               'today_new_clients': today_new_clients,
               'last_month_new_clients': last_month_new_clients,
               'last_month_new_clients_pulkovo': last_month_new_clients_pulkovo,
               'lastMonth': lastMonth,
               # СМС
               'sms_chart': sms_chart[:5]}
    return render(request, 'chart.html', context)


def chart_driver(request, driver_id):
    # Вычисляем максимальный день текущего месяца. Для просмотра архива.
    # max_day_in_current_month = calendar.monthrange(timezone.now().year, timezone.now().month)[1]
    # Определяем периоды для запроса
    current_day = datetime.datetime.now()
    # start_day_current_month = current_day.replace(month=11, day=1, hour=0, minute=0, second=0, microsecond=0)
    start_day_current_month = current_day.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    end_current_day = current_day.replace(hour=23, minute=59, second=59, microsecond=999999)

    # Запрос всех заказов из базы статистики вся база(все с State=7 -оплачен, id = id водителя)
    orders_all_time = TsOrders.objects.using('Cx_TaxiStatistics').filter(state=7,
                                                                         iddriver=driver_id).order_by(
        '-deliverytime')
    # Для regroup по месяцам добавляем месяцы и год в которые работал водитель
    for order in orders_all_time:
        month = order.deliverytime.strftime("%B")
        year = order.deliverytime.strftime("%Y")
        order.month = month
        order.year = year

    # Запрос всех заказов из базы статистики текущего месяца(все с State=7 -оплачен, id = id водителя)
    orders_current_month = TsOrders.objects.using('Cx_TaxiStatistics').filter(
        deliverytime__range=(start_day_current_month, end_current_day), state=7, iddriver=driver_id).order_by(
        '-deliverytime')
    # Добавляем вычисляемые авраметры (скорость, время и тд)
    for order in orders_current_month:
        drive_time = order.laststatetime - order.starttime
        order.drive_time = timedelta(seconds=drive_time.seconds)
        speed = order.distance // (timedelta(seconds=drive_time.seconds).seconds / 3600)
        order.speed = speed
        # Для regroup по датам месяца добавляем даты текущего месяца
        day_of_month = order.deliverytime.strftime("%d %B %y")
        order.day_of_month = day_of_month
        # Добавляем признак корпоративного заказа
        if order.idcorporate:
            corporate_name = Corporations.objects.using('Cx_TaxiConfiguration').get(id=order.idcorporate).name
            order.corporate_name = corporate_name
        else:
            order.corporate_name = None

    # Показываем параметры водителя
    driver = Drivers.objects.using('Cx_TaxiConfiguration').get(id=driver_id)

    context = {'driver': driver,
               'orders_all_time': orders_all_time,
               'orders_current_month': orders_current_month}
    return render(request, 'chart_driver.html', context)


# ----- START ----- КОРП КЛИЕНТЫ ПО ГОДАМ-МЕСЯЦАМ
def chart_corp(request, corp_id):
    test_day = datetime.datetime.now()
    # current_day = test_day.replace(year=2017, month=11, day=19, hour=10, minute=0, second=0)
    current_day = datetime.datetime.now()
    start_day_current_month = current_day.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    start_current_day = current_day.replace(hour=0, minute=0, second=0, microsecond=0)
    end_current_day = current_day.replace(hour=23, minute=59, second=59, microsecond=999999)
    current_year = current_day.year
    current_month = current_day.month

    sum_days_in_current_month = calendar.monthrange(start_day_current_month.year, start_day_current_month.month)[1]
    last_day_of_current_month = current_day.replace(day=sum_days_in_current_month, hour=23, minute=59, second=59,
                                                    microsecond=999)

    one_day = timedelta(days=1)
    yesterday = current_day - one_day
    start_yesterday = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
    end_yesterday = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)

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

    # !!!! ЧАРТ ЗАКАЗЫ КОРП КЛИЕНТА !!!!
    # - Предварительные
    corp_pre_orders = TaOrders.objects.using('Cx_TaxiActive').filter(
        deliverytime__range=(start_day_current_month, last_day_of_current_month), state__in=[1, 14]).filter(
        idcorporate=corp_id).order_by('deliverytime')
    # - Активные
    corp_active_orders = TaOrders.objects.using('Cx_TaxiActive').filter(
        deliverytime__range=(start_day_current_month, last_day_of_current_month), state__in=[3, 4, 5, 7, 11]).filter(
        idcorporate=corp_id).order_by('deliverytime')
    # - Статистика
    corp_orders = TsOrders.objects.using('Cx_TaxiStatistics').filter(
        deliverytime__range=(start_day_current_month, end_current_day), state=7).filter(idcorporate=corp_id).order_by(
        '-deliverytime')

    def today_maker(querry):
        for orders in querry:
            if orders.deliverytime.day == current_day.day:
                orders.today_marker = True
            else:
                orders.today_marker = False

    today_maker(corp_pre_orders)
    today_maker(corp_active_orders)
    today_maker(corp_orders)

    # !!!! КОНЕЦ ЧАРТ ЗАКАЗЫ КОРП КЛИЕНТА !!!!

    # START - Статистические данные
    sum_active = TaOrders.objects.using('Cx_TaxiActive').filter(
        deliverytime__range=(start_day_current_month, last_day_of_current_month), state__in=[3, 4, 5, 7, 11]).filter(
        idcorporate=corp_id).aggregate(Sum('cost'))['cost__sum']
    sum_pre = TaOrders.objects.using('Cx_TaxiActive').filter(
        deliverytime__range=(start_day_current_month, last_day_of_current_month), state__in=[1, 14]).filter(
        idcorporate=corp_id).aggregate(Sum('cost'))['cost__sum']
    sum_today = \
        TsOrders.objects.using('Cx_TaxiStatistics').filter(deliverytime__range=(start_current_day, end_current_day),
                                                           state=7).filter(idcorporate=corp_id).aggregate(Sum('cost'))[
            'cost__sum']
    sum_yesterday = \
        TsOrders.objects.using('Cx_TaxiStatistics').filter(deliverytime__range=(start_yesterday, end_yesterday),
                                                           state=7).filter(idcorporate=corp_id).aggregate(Sum('cost'))[
            'cost__sum']
    sum_month = \
        TsOrders.objects.using('Cx_TaxiStatistics').filter(
            deliverytime__range=(start_day_current_month, end_current_day),
            state=7).filter(idcorporate=corp_id).aggregate(Sum('cost'))[
            'cost__sum']
    sum_month_plan = condition_or_0(sum_active) + condition_or_0(sum_pre) + condition_or_0(sum_month)
    # END - Статистические данные

    corporate_name = Corporations.objects.using('Cx_TaxiConfiguration').get(id=corp_id).name

    context = {'current_year': current_year,
               'current_month': current_month,
               'current_day': current_day,
               'sum_active': sum_active,
               'sum_pre': sum_pre,
               'sum_today': sum_today,
               'sum_yesterday': sum_yesterday,
               'sum_month': sum_month,
               'sum_month_plan': sum_month_plan,
               'corp_id': corp_id,
               'corporate_name': corporate_name,
               'corp_orders': corp_orders,
               'corp_active_orders': corp_active_orders,
               'corp_pre_orders': corp_pre_orders,
               }
    return render(request, 'chart_corp.html', context)
# ----- END ----- КОРП КЛИЕНТЫ ПО ГОДАМ-МЕСЯЦАМ
