from django.shortcuts import render, HttpResponseRedirect
from django.contrib import auth
from django.db.models import Max
from django.http import Http404
import datetime
from datetime import timedelta
import calendar
import operator

from infinity.models import TsOrders, TaOrders, Drivers, Parkings, Corporations, Cars, Drivercontacts, TsCarstatechanges
from smena.models import Run


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


# Список водителей, отключенных  от показа (Гаркуша)
driver_list_my_block = [5018737745]
driver_list_my_block_names = []
for id in driver_list_my_block:
    name = Drivers.objects.using('Cx_TaxiConfiguration').get(id=id).fullname
    driver_list_my_block_names.append(name)


# Определяем водителей "на линии". Если сидит в машине, значит online
def driver_online(diver_id):
    cars = Cars.objects.using('Cx_TaxiConfiguration').filter(idcurrentdriver=diver_id)
    if cars:
        driver_status = 1
    else:
        driver_status = 0
    return driver_status


# собираем список id копративщиков, где есть ИНН для использования вхождения __in в запросе
corporate_list_id = [int(i['id']) for i in
                     Corporations.objects.using('Cx_TaxiConfiguration').filter(inn__isnull=False).values('id')]
# тоже самое без ИНН
corporate_list_id_no_inn = [int(i['id']) for i in
                            Corporations.objects.using('Cx_TaxiConfiguration').filter(inn__isnull=True).values('id')]


# Статус автомобиля
def car_state(state):
    state_rus = 'Без статуса'
    if state == 1:
        state_rus = 'Отключен'
    elif state == 2:
        state_rus = 'На линии'
    elif state == 3:
        state_rus = 'На заказе'
    elif state == 4:
        state_rus = 'Перерыв'
    elif state == 5:
        state_rus = 'Поломка'
    elif state == 7:
        state_rus = 'Назначен на заказ'
    return state_rus


def strfdelta(tdelta):
    d = {"days": tdelta.days}
    d["hours"], rem = divmod(tdelta.seconds, 3600)
    d["minutes"], d["seconds"] = divmod(rem, 60)
    if tdelta.days == 0:
        return '{hours} часа {minutes} минут'.format(**d)
    else:
        return '{days} дней {hours} часа {minutes} минут'.format(**d)


# ------ КОНЕЦ ОБЩИЕ ПЕРЕМЕННЫЕ И ФУНКЦИИ -----------

def drivers(request):
    # Список id работающих водителей из таблицы водителей (isblocked!=1)
    driver_list_work_id = list([int(i['id']) for i in
                                Drivers.objects.using('Cx_TaxiConfiguration').exclude(isblocked=1).exclude(
                                    isdeleted=1).exclude(id__in=driver_list_my_block).values('id')])

    driver_chart = []
    for driver_id in driver_list_work_id:
        driver_dict = dict()
        driver_dict['fullname'] = Drivers.objects.using('Cx_TaxiConfiguration').get(id=driver_id).fullname

        try:
            driver_dict['phone'] = \
                Drivercontacts.objects.using('Cx_TaxiConfiguration').filter(idabonent=driver_id).filter(isdefault=1)[
                    0].contact
        except:
            driver_dict['phone'] = ''
        cars = Cars.objects.using('Cx_TaxiConfiguration').filter(idcurrentdriver=driver_id)
        if cars:
            driver_dict['carmodel'] = cars[0].idmodel.name
            driver_dict['number'] = cars[0].number
            driver_dict['color'] = cars[0].idcolor.name
            driver_dict['online'] = driver_online(driver_id)
        driver_dict['online_sort'] = False if driver_online(driver_id) else True
        driver_chart.append(driver_dict)
    # Сортируем по fullname + online_sort
    sort_fullname_chart = []
    for i in sorted(driver_chart, key=operator.itemgetter("fullname")):
        sort_fullname_chart.append(i)
    sort_online_chart = []
    for i in sorted(sort_fullname_chart, key=operator.itemgetter("online_sort")):
        sort_online_chart.append(i)

    context = {'driver_chart': sort_online_chart,
               'driver_active': True}
    return render(request, 'drivers.html', context)


def cars(request):
    current_day = datetime.datetime.now()
    # current_day = datetime.datetime(year=2017, month=12, day=10, hour=5)

    cars = Cars.objects.using('Cx_TaxiConfiguration')
    runs = Run.objects.order_by('finish_km')

    cars_chart = []
    for car in cars:
        cars_dict = dict()
        cars_dict['id'] = car.id
        cars_dict['callsign'] = car.callsign
        cars_dict['number'] = car.number
        cars_dict['idmodel'] = car.idmodel
        cars_dict['idcolor'] = car.idcolor
        cars_dict['age'] = car.age
        if runs.filter(car_id=car.id).last():
            cars_dict['run'] = '{0:,}'.format(
                runs.filter(car_id=car.id).aggregate(Max('finish_km'))['finish_km__max']).replace(',', ' ')
        else:
            cars_dict['run'] = 'Нет данных'
        cars_dict['idparking'] = car.idparking
        try:
            cars_dict['destination_zone_name'] = TaOrders.objects.using('Cx_TaxiActive').get(idcar=car.id, state__gt=1,
                                                                                             state__lte=5).destinationzonestr
        except:
            cars_dict['destination_zone_name'] = ''
        cars_dict['idcurrentdriver'] = car.idcurrentdriver
        cars_dict['state_rus'] = car_state(car.state)
        cars_dict['state'] = car.state
        if car.statestarttime:
            s_time = current_day - car.statestarttime
        else:
            continue
        cars_dict['status_time'] = strfdelta(s_time)
        cars_dict['start_online_time'] = car.timeonline
        on_time = current_day - car.timeonline
        cars_dict['online_time'] = strfdelta(on_time) if car.idcurrentdriver else strfdelta(
            (car.timedisconnected if car.timedisconnected else current_day) - car.timeonline)
        cars_dict['end_online_time'] = '-' if car.idcurrentdriver else (
            car.timedisconnected if car.timedisconnected else 'Нет данных')
        cars_dict['online'] = True if car.idcurrentdriver else False
        cars_chart.append(cars_dict)

    # Сортируем по callsign + online_sort
    sort_cars_chart = []
    for i in sorted(cars_chart, key=operator.itemgetter("callsign")):
        sort_cars_chart.append(i)
    sort_online_chart = []
    for i in sorted(sort_cars_chart, key=operator.itemgetter("online"), reverse=True):
        sort_online_chart.append(i)

    context = {'cars_chart': sort_online_chart,
               'car_active': True}
    return render(request, 'cars.html', context)
