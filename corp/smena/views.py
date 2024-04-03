from django.shortcuts import render, render_to_response, get_object_or_404, HttpResponseRedirect
from django.contrib import auth
from django.db.models import Sum, Count, Min, Max
from django.http import Http404
from django.utils import timezone
from datetime import timedelta
import datetime
import operator

from infinity.models import TsOrders, Drivers, Corporations, Cars
from complaints.models import Complaint
from .forms import SmenaForm, RunForm
from .models import Smena, Run


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


# ----------- ГЛОМАЛЬНЫЕ ПЕРЕМЕННЫЕ И ФУНКЦИИ ------------------------ #
current_day = datetime.datetime.today()
first_start_day = current_day.replace(year=2017, month=10, day=1, hour=0, minute=0, second=1)
start_current_day = current_day.replace(hour=0, minute=0, second=0, microsecond=0)
end_current_day = current_day.replace(hour=10, minute=00, second=00, microsecond=0)
second_plus_one = timedelta(seconds=1)

# собираем список id копративщиков, где есть ИНН для использования вхождения __in в запросе
corporate_list_id = [int(i['id']) for i in
                     Corporations.objects.using('Cx_TaxiConfiguration').filter(inn__isnull=False).values('id')]
# тоже самое без ИНН
corporate_list_id_no_inn = [int(i['id']) for i in
                            Corporations.objects.using('Cx_TaxiConfiguration').filter(inn__isnull=True).values(
                                'id')]


# Расшифровка и покраска заказов за период, справа в SMENA_CU.HTML
def orders_per_period_in_color(period):
    for order in period:
        # Разделяем выручку по способам оплаты
        if order.isnotcash == 0 and order.payedwithcard == 0:
            order.pay_method = 'наличные'
        elif order.isnotcash == 0 and order.payedwithcard is None:
            order.pay_method = 'наличные'
        elif order.isnotcash in [None, 0] and order.payedwithcard == 1:
            order.pay_method = 'терминал'
        elif order.idcorporate in corporate_list_id:
            order.pay_method = 'безнал'
        elif order.idcorporate in corporate_list_id_no_inn and order.isnotcash == 1:
            order.pay_method = 'безнал'
        elif order.isnotcash == 1 and order.idcorporate is None:
            order.pay_method = 'сайт'
        else:
            order.pay_method = 'Не определено' + ', isnotcash:' + str(order.isnotcash) + ', card:' + str(
                order.payedwithcard) + ', corp:' + str(order.idcorporate)
        # Добавляем признак корпоративного заказа
        if order.idcorporate:
            order.corporate_name = Corporations.objects.using('Cx_TaxiConfiguration').get(
                id=order.idcorporate).name
        else:
            order.corporate_name = None
        # Добавляем признак корпоративного клиента без ИНН
        if order.idcorporate in corporate_list_id_no_inn:
            order.no_inn = 1
    return order


# Запрос списка словарей уникальных авто за период заказов
def get_cars_in_range(range_query, smena_id=None):
    orders = range_query.distinct('idcar')
    cars_chart = []
    for order in orders:
        cars = Cars.objects.using('Cx_TaxiConfiguration').filter(id=order.idcar)
        for car in cars:
            car_dict = dict()
            car_dict['id'] = car.id
            car_dict['callsign'] = car.callsign
            car_dict['idmodel'] = car.idmodel
            car_dict['number'] = car.number
            car_dict['from'] = range_query.filter(idcar=car.id).order_by('deliverytime')[0].deliverytime
            car_dict['to'] = range_query.filter(idcar=car.id).order_by('-deliverytime')[0].deliverytime
            car_dict['orders'] = range_query.filter(idcar=car.id).count()
            try:
                car_dict['start_km'] = Run.objects.filter(car_id=car.id).aggregate(Max('finish_km'))['finish_km__max']
                if car_dict['start_km'] is None:
                    car_dict['start_km'] = 0
            except:
                car_dict['start_km'] = 0
            # Для view UPDATE
            if smena_id:
                try:
                    car_dict['run'] = Run.objects.get(car_id=car.id, smena_id=smena_id).run
                    car_dict['start_km'] = Run.objects.get(car_id=car.id, smena_id=smena_id).start_km
                    car_dict['finish_km'] = Run.objects.get(car_id=car.id, smena_id=smena_id).finish_km
                except:
                    car_dict['run'] = 0
                    car_dict['start_km'] = 0
                    car_dict['finish_km'] = 0
            cars_chart.append(car_dict)
    sorted_cars_chart = []
    for i in sorted(cars_chart, key=operator.itemgetter("from")):
        sorted_cars_chart.append(i)
    return sorted_cars_chart


def condition_or_0(condition):
    if condition:
        return float(condition)
    else:
        return 0


# ------------------------- ГЛАВНАЯ СТРАНИЦА ЗАКРЫТИЯ СМЕНЫ ----------------------
def smena(request):
    # Инициируем заново переменные с временем, т.к. нужно актуальное время
    current_day = datetime.datetime.today()
    end_current_day = current_day.replace(hour=10, minute=00, second=00, microsecond=0)

    # Запрос всех заказов из базы статистики (все с State=7 -оплачен)
    def get_orders(start_day, end_day):
        orders_current_day = TsOrders.objects.using('Cx_TaxiStatistics').filter(
            deliverytime__range=(start_day, end_day),
            state=7)
        return orders_current_day

    # Список водителей, отключенных  от показа (Гаркуша, Федоров, Ушаков, Степанов)
    driver_list_my_block = [5018737745, 5042082447, 5011597095, 5017290831]
    driver_list_my_block_names = []
    for id in driver_list_my_block:
        name = Drivers.objects.using('Cx_TaxiConfiguration').get(id=id).fullname
        driver_list_my_block_names.append(name)

    # Список id работающих водителей из таблицы водителей (isblocked!=1)
    driver_list_work_id = list([int(i['id']) for i in
                                Drivers.objects.using('Cx_TaxiConfiguration').exclude(isblocked=1).exclude(
                                    id__in=driver_list_my_block).values(
                                    'id')])

    # Запрос данных из базы "закрытие смены"
    def get_smena(iddriver):
        smena_chart = Smena.objects.filter(driver_id=iddriver)
        return smena_chart

    # Собираем список id водителей, которые работали за период+фильтр что не заблокированы
    # Множество(set), чтобы убрать повторения id
    driver_list_id = set(
        list([int(i['iddriver']) for i in
              get_orders(first_start_day, end_current_day).filter(iddriver__in=driver_list_work_id).values(
                  'iddriver')]))

    # Определяем водителей "на линии". Если сидит в машине, значит online
    def driver_online(diver_id):
        cars = Cars.objects.using('Cx_TaxiConfiguration').filter(idcurrentdriver=diver_id)
        if cars:
            driver_status = 1
        else:
            driver_status = 0
        return driver_status

    # Всего на руках у всех водителей
    all_hand_cash = 0

    # smena_dict['status']:
    # 0 - первичный ввод
    # 1 - новый водитель
    # 2 - стандартное закрытие
    # 3 - редактирование закрытой смены
    drvier_chart = []
    for driver_id in driver_list_id:
        smena_chart = []
        driver_dict = dict()
        driver_dict['iddriver'] = driver_id
        driver_name = Drivers.objects.using('Cx_TaxiConfiguration').get(id=driver_id).fullname
        driver_dict['fullname'] = driver_name.split()
        driver_dict['open_complaints'] = Complaint.objects.all().filter(driver_id=driver_id, complaint_status_id__in=[1, 2]).count
        driver_dict['driver_on_off'] = driver_online(driver_id)
        try:
            last_smenas = Smena.objects.filter(driver_id=driver_id).order_by('-date')[:3]
            last_smena = Smena.objects.filter(driver_id=driver_id).order_by('-date')[0]
            driver_dict['count_days_last_smena'] = (current_day - last_smena.finish_date.replace(hour=0)).days
            for smena in last_smenas:
                smena_dict = dict()
                smena_dict['smena_id'] = smena.id
                smena_dict['number'] = smena.number
                smena_dict['date'] = smena.date
                smena_dict['run'] = Run.objects.filter(smena_id=smena.id).aggregate(Sum('run'))['run__sum']
                smena_dict['fuel_consumption'] = smena.fuel_consumption
                smena_dict['money_to_boss_fact'] = smena.money_to_boss_fact
                smena_dict['debt'] = smena.debt
                smena_dict['proceeds_terminal'] = smena.proceeds_terminal
                smena_dict['proceeds_corporate_bank'] = smena.proceeds_corporate_bank
                smena_dict['spending'] = smena.spending
                smena_dict['start_date'] = smena.start_date
                smena_dict['finish_date'] = smena.finish_date
                smena_dict['delta_days'] = (smena.finish_date - smena.start_date).days
                smena_dict['delta_cash'] = condition_or_0(
                    get_orders(smena.start_date, smena.finish_date).filter(iddriver=driver_id).aggregate(Sum('cost'))[
                        'cost__sum'])
                smena_chart.append(smena_dict)
            driver_dict['smena_chart'] = smena_chart
            driver_dict['cash'] = condition_or_0(TsOrders.objects.using('Cx_TaxiStatistics').filter(
                deliverytime__range=(last_smena.finish_date + second_plus_one, end_current_day), state=7).filter(
                iddriver=driver_id).filter(isnotcash=0).exclude(payedwithcard=1).aggregate(
                Sum('cost'))['cost__sum'])
            driver_dict['status'] = 2
            all_hand_cash += driver_dict['cash']
        except:
            # Если заказов от стартового периода заказов больше 100, то первичные данные иначе новый водитель с суммой
            if TsOrders.objects.using('Cx_TaxiStatistics').filter(
                    deliverytime__range=(first_start_day, end_current_day), state=7).filter(
                iddriver=driver_id).count() > 100:
                driver_dict['status'] = 0
                driver_dict['cash'] = 'Нет данных'
            else:
                driver_dict['cash'] = condition_or_0(TsOrders.objects.using('Cx_TaxiStatistics').filter(
                    deliverytime__range=(first_start_day, end_current_day), state=7).filter(iddriver=driver_id).filter(
                    isnotcash=0).exclude(payedwithcard=1).aggregate(Sum('cost'))['cost__sum'])
                driver_dict['status'] = 1
            driver_dict['last_smena'] = 'Нет данных'
        drvier_chart.append(driver_dict)

    # Сортируем по fullname
    sort_fullname_chart = []
    for i in sorted(drvier_chart, key=operator.itemgetter("fullname")):
        sort_fullname_chart.append(i)
    context = {'driver_chart': sort_fullname_chart,
               'end_current_day': end_current_day,
               'all_hand_cash': all_hand_cash,
               'driver_list_my_block_names': driver_list_my_block_names}

    return render(request, 'smena.html', context)


# ----------------- СОЗДАНИЕ СМЕНЫ --------------------

def smena_create(request, driver_id, status, year=None, month=None, day=None, hour=None, min=None):
    # Для перерасчёта закрытой смены вводим smena_id
    smena_id = None
    last_smena = None
    # Перерасчёт текущей смены ВКЛ
    recalculation = 1

    driver_fullname = Drivers.objects.using('Cx_TaxiConfiguration').get(id=driver_id).fullname

    # Запрос всех заказов из базы статистики (все с State=7 -оплачен)
    def get_orders(start_day, end_day, iddriver):
        orders_current_day = TsOrders.objects.using('Cx_TaxiStatistics').filter(iddriver=iddriver).filter(
            deliverytime__range=(start_day, end_day), state=7)
        return orders_current_day

    if year:
        finish_date = datetime.datetime.now().replace(year=year, month=month, day=day, hour=hour, minute=min, second=0,
                                                      microsecond=0)
    else:
        # Дата по-умолчанию для закрытия смены. Сегодня в 10:00
        finish_date = datetime.datetime.now().replace(hour=10, minute=0, second=0, microsecond=0)

    start_date = datetime.datetime.now()
    # status:
    # 0 - первичный ввод
    # 1 - новый водитель
    # 2 - стандартное закрытие
    # 3 - редактирование закрытой смены
    if status == 0:
        start_date = first_start_day
        finish_date = end_current_day
    if status == 1:
        start_date = first_start_day
        finish_date = end_current_day
    if status == 2:
        start_date = Smena.objects.filter(driver_id=driver_id).order_by('-date')[
                         0].finish_date + second_plus_one
        # finish_date = end_current_day
    if status == 3:
        last_smena = Smena.objects.filter(driver_id=driver_id).order_by('-date')[0]
        start_date = last_smena.start_date
        # finish_date = last_smena.finish_date
        if smena_id != last_smena.id:
            recalculation = 0


    if request.method == 'POST':
        form = SmenaForm(request.POST)
        if form.is_valid():
            # После редактирования последней смены, удаляем старый вариант смены
            if status == 3:
                smena = get_object_or_404(Smena, id=last_smena.id)
                smena.delete()
            post = form.save(commit=False)
            post.number = Smena.objects.count() + 1
            post.date = datetime.date.today()
            post.driver_id = driver_id
            post.start_date = request.POST.get('start_date')
            if status == 3:
                post.finish_date = finish_date
            else:
                post.finish_date = request.POST.get('finish_date')
            post.proceeds_cash = condition_or_0(request.POST.get('proceeds_cash'))
            post.proceeds_cash_orders = condition_or_0(request.POST.get('proceeds_cash_orders'))
            post.proceeds_terminal = condition_or_0(request.POST.get('proceeds_terminal'))
            post.proceeds_terminal_orders = condition_or_0(request.POST.get('proceeds_terminal_orders'))
            post.proceeds_corporate_bank = condition_or_0(request.POST.get('proceeds_corporate_bank'))
            post.proceeds_corporate_bank_orders = condition_or_0(request.POST.get('proceeds_corporate_bank_orders'))
            post.proceeds = int(post.proceeds_cash) + int(post.proceeds_terminal) + int(
                post.proceeds_corporate_bank)
            post.spending_fuel_cash = condition_or_0(request.POST.get('spending_fuel_cash'))
            post.spending_fuel_litres = condition_or_0(request.POST.get('spending_fuel_litres'))
            post.fuel_consumption = condition_or_0(request.POST.get('fuel_consumption'))
            post.spending_carwash = condition_or_0(request.POST.get('spending_carwash'))
            post.spending_carwash_bank = condition_or_0(request.POST.get('spending_carwash_bank'))
            post.spending_parking = condition_or_0(request.POST.get('spending_parking'))
            post.spending_washer = condition_or_0(request.POST.get('spending_washer'))
            post.spending_to = condition_or_0(request.POST.get('spending_to'))
            post.spending_lamp = condition_or_0(request.POST.get('spending_lamp'))
            post.spending_repair = condition_or_0(request.POST.get('spending_repair'))
            post.spending_etc = condition_or_0(request.POST.get('spending_etc'))
            post.spending_etc_comment = request.POST.get('spending_etc_comment')
            post.spending = int(post.spending_fuel_cash) + int(post.spending_carwash) + int(
                post.spending_parking) + int(post.spending_washer) + int(post.spending_to) + int(
                post.spending_lamp) + int(post.spending_repair) + int(post.spending_etc)
            post.money_to_boss = condition_or_0(request.POST.get('money_to_boss'))
            post.money_to_boss_fact = condition_or_0(request.POST.get('money_to_boss_fact'))
            post.debt = condition_or_0(request.POST.get('debt'))
            post.debt_comment = request.POST.get('debt_comment')
            post.save()
        # Сохраняем Пробеги в другу модельку
        # Запрос для кол-ва машин и id машин в форме
        cars_chart = get_cars_in_range(get_orders(start_date, finish_date, driver_id))
        # ТУТ ТРЕШ !!!!!!!!! ПОКА НЕ ЗНАЮ КАК СДЕЛАТЬ ЛУЧШЕ. Рассчитано на 4 авто !!!
        car_count = 0
        for car in cars_chart:
            if car_count == 1:
                run_form = RunForm(request.POST)
                if run_form.is_valid():
                    post = run_form.save(commit=False)
                    # Берем из БД последнюю сохр. смену (плохое решение)
                    post.smena_id = Smena.objects.last()
                    post.car_id = car['id']
                    post.run = condition_or_0(request.POST.get('run_2'))
                    post.start_km = condition_or_0(request.POST.get('start_km_2'))
                    post.finish_km = condition_or_0(request.POST.get('finish_km_2'))
                    post.save()
                    car_count += 1
                    continue
            if car_count == 2:
                run_form = RunForm(request.POST)
                if run_form.is_valid():
                    post = run_form.save(commit=False)
                    # Берем из БД последнюю сохр. смену (плохое решение)
                    post.smena_id = Smena.objects.last()
                    post.car_id = car['id']
                    post.run = condition_or_0(request.POST.get('run_3'))
                    post.start_km = condition_or_0(request.POST.get('start_km_3'))
                    post.finish_km = condition_or_0(request.POST.get('finish_km_3'))
                    post.save()
                    car_count += 1
                    continue
            if car_count == 3:
                run_form = RunForm(request.POST)
                if run_form.is_valid():
                    post = run_form.save(commit=False)
                    # Берем из БД последнюю сохр. смену (плохое решение)
                    post.smena_id = Smena.objects.last()
                    post.car_id = car['id']
                    post.run = condition_or_0(request.POST.get('run_4'))
                    post.start_km = condition_or_0(request.POST.get('start_km_4'))
                    post.finish_km = condition_or_0(request.POST.get('finish_km_4'))
                    post.save()
                    car_count += 1
                    continue
            run_form = RunForm(request.POST)
            if run_form.is_valid():
                post = run_form.save(commit=False)
                # Берем из БД последнюю сохр. смену (плохое решение)
                post.smena_id = Smena.objects.last()
                post.car_id = car['id']
                post.run = condition_or_0(request.POST.get('run_1'))
                post.start_km = condition_or_0(request.POST.get('start_km_1'))
                post.finish_km = condition_or_0(request.POST.get('finish_km_1'))
                post.save()
                car_count += 1
            # !!!!!! КОНЕЦ ТРЕША !!!!!!!!
        return HttpResponseRedirect('/smena')
    else:

        form = SmenaForm()
        #
        # --------------- АНАЛИТИКА Cx_TaxiStatistics ----------------
        #
        # ВСЕ Выполненные по категориям за период
        all_money_current_smena = condition_or_0(
            get_orders(start_date, finish_date, driver_id).aggregate(Sum('cost'))['cost__sum'])
        all_orders_current_smena = get_orders(start_date, finish_date, driver_id).count()
        # НАЛ
        all_money_cash = condition_or_0(
            get_orders(start_date, finish_date, driver_id).filter(isnotcash=0).filter(
                idcorporate__isnull=True).exclude(payedwithcard=1).aggregate(Sum('cost'))['cost__sum'])
        all_orders_cash = get_orders(start_date, finish_date, driver_id).filter(isnotcash=0).filter(
            idcorporate__isnull=True).exclude(payedwithcard=1).count()
        # ТЕРМИНАЛ
        all_money_terminal = condition_or_0(
            get_orders(start_date, finish_date, driver_id).filter(payedwithcard=1).aggregate(
                Sum('cost'))['cost__sum'])
        all_orders_terminal = get_orders(start_date, finish_date, driver_id).filter(
            payedwithcard=1).count()
        # корп безнал с ИНН
        all_money_corp = condition_or_0(
            get_orders(start_date, finish_date, driver_id).filter(idcorporate__in=corporate_list_id).aggregate(
                Sum('cost'))['cost__sum'])
        all_orders_corp = get_orders(start_date, finish_date, driver_id).filter(
            idcorporate__in=corporate_list_id).count()
        # САЙТ
        all_money_site_pay = condition_or_0(
            get_orders(start_date, finish_date, driver_id).filter(isnotcash=1).filter(
                idcorporate__isnull=True).aggregate(Sum('cost'))['cost__sum'])
        all_orders_site_pay = get_orders(start_date, finish_date, driver_id).filter(isnotcash=1).filter(
            idcorporate__isnull=True).count()
        # Корпоратив без ИНН (ЗАКАЗЫ НА ОФИС - кидаем впоследствии в БЕЗНАЛ)
        all_corp_money_current_day_no_inn_beznal = condition_or_0(
            get_orders(start_date, finish_date, driver_id).filter(
                idcorporate__in=corporate_list_id_no_inn).filter(isnotcash=1).aggregate(Sum('cost'))['cost__sum'])
        all_corp_orders_current_day_no_inn_beznal = get_orders(start_date, finish_date, driver_id).filter(
            idcorporate__in=corporate_list_id_no_inn).filter(isnotcash=1).count()
        # Корпоратив без ИНН (НАЛ)
        all_corp_money_current_day_no_inn_cash = condition_or_0(
            get_orders(start_date, finish_date, driver_id).filter(
                idcorporate__in=corporate_list_id_no_inn).filter(isnotcash=0).exclude(payedwithcard=1).aggregate(
                Sum('cost'))['cost__sum'])
        all_corp_orders_current_day_no_inn_cash = get_orders(start_date, finish_date, driver_id).filter(
            idcorporate__in=corporate_list_id_no_inn).filter(isnotcash=0).exclude(payedwithcard=1).count()
        # Список словарей уникальных авто за период
        cars_chart = get_cars_in_range(get_orders(start_date, finish_date, driver_id))

        # Итого наличные к сдаче: ф.л.Нал + Нал Корп без ИНН
        # Данные уходят в SMENA_CU.HTML
        proceeds_cash = all_money_cash + all_corp_money_current_day_no_inn_cash
        proceeds_cash_orders = all_orders_cash + all_corp_orders_current_day_no_inn_cash
        # Итого банковский терминал: Ф.л.Терминал + Корп без ИНН Терминал. Все с payedwithcard=1
        proceeds_terminal = all_money_terminal
        proceeds_terminal_orders = all_orders_terminal
        # Итого безналичный расчёт: Корп с ИНН + Сайт + Корпоратив без ИНН (ОФИС)
        proceeds_corporate_bank = all_money_corp + all_money_site_pay + all_corp_money_current_day_no_inn_beznal
        proceeds_corporate_bank_orders = all_orders_corp + all_orders_site_pay + all_corp_orders_current_day_no_inn_beznal

        # Запрос всех заказов из базы статистики за заданный период(все с State=7 -оплачен, id = id водителя)
        orders_current_smena = get_orders(start_date, finish_date, driver_id).order_by('deliverytime')
        if orders_current_smena:
            orders_per_period_in_color(orders_current_smena)

        # Добавление ДОЛГА из прошлой закрытой смены, если он есть
        try:
            last_smena_for_debt = Smena.objects.filter(driver_id=driver_id).order_by('-date')[0]
            debt_last_smena = last_smena_for_debt.debt
            debt_last_smena_comment = last_smena_for_debt.debt_comment
        except:
            debt_last_smena = 0
            debt_last_smena_comment = None

    context = {'time': datetime.datetime.now(),
               'recalculation': recalculation,
               'smena_id': smena_id,
               'smena': last_smena,
               'driver_id': driver_id,
               'driver_fullname': driver_fullname,
               'status': status,
               'start_date': start_date,
               'finish_date': finish_date,
               'all_money_current_smena': all_money_current_smena, 'all_orders_current_smena': all_orders_current_smena,
               'proceeds_cash': proceeds_cash, 'proceeds_cash_orders': proceeds_cash_orders,
               'proceeds_terminal': proceeds_terminal, 'proceeds_terminal_orders': proceeds_terminal_orders,
               'proceeds_corporate_bank': proceeds_corporate_bank,
               'proceeds_corporate_bank_orders': proceeds_corporate_bank_orders,
               'orders_current_smena': orders_current_smena,
               'form': form,
               'cars_chart': cars_chart,
               'debt_last_smena': debt_last_smena,
               'debt_last_smena_comment': debt_last_smena_comment
               }
    return render(request, 'smena_cu.html', context)


# РЕДАКТИРОВАНИЕ СМЕНЫ
def smena_update(request, smena_id):
    # Редактирование смены
    status = 3

    def get_orders(start_day, end_day, iddriver):
        orders_current_day = TsOrders.objects.using('Cx_TaxiStatistics').filter(iddriver=iddriver).filter(
            deliverytime__range=(start_day, end_day), state=7)
        return orders_current_day

    smena = get_object_or_404(Smena, id=smena_id)

    recalculation = None
    last_smena = Smena.objects.filter(driver_id=smena.driver_id).order_by('-date')[0]
    if smena_id == last_smena.id:
        recalculation = 1

    if request.method == 'POST':
        form = SmenaForm(request.POST, instance=smena)
        if form.is_valid():
            post = form.save(commit=False)
            # post.start_date = request.POST.get('start_date')
            # post.finish_date = request.POST.get('finish_date')
            post.proceeds_cash = condition_or_0(request.POST.get('proceeds_cash'))
            post.proceeds_cash_orders = condition_or_0(request.POST.get('proceeds_cash_orders'))
            post.proceeds_terminal = condition_or_0(request.POST.get('proceeds_terminal'))
            post.proceeds_terminal_orders = condition_or_0(request.POST.get('proceeds_terminal_orders'))
            post.proceeds_corporate_bank = condition_or_0(request.POST.get('proceeds_corporate_bank'))
            post.proceeds_corporate_bank_orders = condition_or_0(request.POST.get('proceeds_corporate_bank_orders'))
            post.proceeds = int(post.proceeds_cash) + int(post.proceeds_terminal) + int(
                post.proceeds_corporate_bank)
            post.spending_fuel_cash = condition_or_0(request.POST.get('spending_fuel_cash'))
            post.spending_fuel_litres = condition_or_0(request.POST.get('spending_fuel_litres'))
            post.fuel_consumption = condition_or_0(request.POST.get('fuel_consumption'))
            post.spending_carwash = condition_or_0(request.POST.get('spending_carwash'))
            post.spending_carwash_bank = condition_or_0(request.POST.get('spending_carwash_bank'))
            post.spending_parking = condition_or_0(request.POST.get('spending_parking'))
            post.spending_washer = condition_or_0(request.POST.get('spending_washer'))
            post.spending_to = condition_or_0(request.POST.get('spending_to'))
            post.spending_lamp = condition_or_0(request.POST.get('spending_lamp'))
            post.spending_repair = condition_or_0(request.POST.get('spending_repair'))
            post.spending_etc = condition_or_0(request.POST.get('spending_etc'))
            post.spending_etc_comment = request.POST.get('spending_etc_comment')
            post.spending = int(post.spending_fuel_cash) + int(post.spending_carwash) + int(
                post.spending_parking) + int(post.spending_washer) + int(post.spending_to) + int(
                post.spending_lamp) + int(post.spending_repair) + int(post.spending_etc)
            post.money_to_boss = condition_or_0(request.POST.get('money_to_boss'))
            post.money_to_boss_fact = condition_or_0(request.POST.get('money_to_boss_fact'))
            post.debt = condition_or_0(request.POST.get('debt'))
            post.debt_comment = request.POST.get('debt_comment')
            post.save()
            # ТУТ ТРЕШ !!!!!!!!! ПОКА НЕ ЗНАЮ КАК СДЕЛАТЬ ЛУЧШЕ. Рассчитано на 4 авто !!!
            cars_chart = get_cars_in_range(get_orders(smena.start_date, smena.finish_date, smena.driver_id))
            car_count = 0
            for car in cars_chart:
                run = get_object_or_404(Run, car_id=car['id'], smena_id=smena_id)
                if car_count == 1:
                    run_form = RunForm(request.POST, instance=run)
                    if run_form.is_valid():
                        post = run_form.save(commit=False)
                        post.run = condition_or_0(request.POST.get('run_2'))
                        post.start_km = condition_or_0(request.POST.get('start_km_2'))
                        post.finish_km = condition_or_0(request.POST.get('finish_km_2'))
                        post.save()
                        car_count += 1
                        continue
                if car_count == 2:
                    run_form = RunForm(request.POST, instance=run)
                    if run_form.is_valid():
                        post = run_form.save(commit=False)
                        post.run = condition_or_0(request.POST.get('run_3'))
                        post.start_km = condition_or_0(request.POST.get('start_km_3'))
                        post.finish_km = condition_or_0(request.POST.get('finish_km_3'))
                        post.save()
                        car_count += 1
                        continue
                if car_count == 3:
                    run_form = RunForm(request.POST, instance=run)
                    if run_form.is_valid():
                        post = run_form.save(commit=False)
                        post.run = condition_or_0(request.POST.get('run_4'))
                        post.start_km = condition_or_0(request.POST.get('start_km_4'))
                        post.finish_km = condition_or_0(request.POST.get('finish_km_4'))
                        post.save()
                        car_count += 1
                        continue
                run_form = RunForm(request.POST, instance=run)
                if run_form.is_valid():
                    post = run_form.save(commit=False)
                    post.run = condition_or_0(request.POST.get('run_1'))
                    post.start_km = condition_or_0(request.POST.get('start_km_1'))
                    post.finish_km = condition_or_0(request.POST.get('finish_km_1'))
                    post.save()
                    car_count += 1
                # !!!!!! КОНЕЦ ТРЕША !!!!!!!!
            return HttpResponseRedirect('/smena')
    else:
        form = SmenaForm()

        driver_id = smena.driver_id
        driver_fullname = Drivers.objects.using('Cx_TaxiConfiguration').get(id=driver_id).fullname
        start_date = smena.start_date
        finish_date = smena.finish_date
        proceeds_cash = smena.proceeds_cash
        proceeds_cash_orders = smena.proceeds_cash_orders
        proceeds_terminal = smena.proceeds_terminal
        proceeds_terminal_orders = smena.proceeds_terminal_orders
        proceeds_corporate_bank = smena.proceeds_corporate_bank
        proceeds_corporate_bank_orders = smena.proceeds_corporate_bank_orders
        orders_current_smena = get_orders(start_date, finish_date, driver_id).order_by('deliverytime')
        # Расшифровка заказов за период, справа в SMENA_CU.HTML
        if orders_current_smena:
            orders_per_period_in_color(orders_current_smena)
        # ВСЕ Выполненные по категориям за период
        all_money_current_smena = condition_or_0(
            get_orders(start_date, finish_date, driver_id).aggregate(Sum('cost'))['cost__sum'])
        all_orders_current_smena = get_orders(start_date, finish_date, driver_id).count()
        # Список словарей уникальных авто за период
        cars_chart = get_cars_in_range(get_orders(start_date, finish_date, driver_id), smena_id)

        context = {'time': datetime.datetime.now(),
                   'status': status,
                   'recalculation': recalculation,
                   'smena_id': smena_id,
                   'smena': smena,
                   'driver_id': driver_id,
                   'driver_fullname': driver_fullname,
                   'start_date': start_date,
                   'finish_date': finish_date,
                   'all_money_current_smena': all_money_current_smena,
                   'all_orders_current_smena': all_orders_current_smena,
                   'proceeds_cash': proceeds_cash, 'proceeds_cash_orders': proceeds_cash_orders,
                   'proceeds_terminal': proceeds_terminal, 'proceeds_terminal_orders': proceeds_terminal_orders,
                   'proceeds_corporate_bank': proceeds_corporate_bank,
                   'proceeds_corporate_bank_orders': proceeds_corporate_bank_orders,
                   'orders_current_smena': orders_current_smena,
                   'form': form,
                   'cars_chart': cars_chart,
                   }
        return render(request, 'smena_cu.html', context)


# Удаление смены
def smena_delete(request, smena_id):
    smena = get_object_or_404(Smena, id=smena_id)
    smena.delete()
    return HttpResponseRedirect('/smena')
