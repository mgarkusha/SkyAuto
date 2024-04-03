import calendar
import datetime
from datetime import timedelta

from django.contrib import auth
from django.db.models import Sum, Count
from django.http import Http404
from django.shortcuts import render, HttpResponseRedirect, get_object_or_404
from infinity.models import Cars

from .forms import PriceForm, OrderForm
from .models import Order, Price


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
# Число последнего дня месяца
def last_day_of_month(year, month):
    sum_days_in_month = calendar.monthrange(datetime.datetime(year=year, month=month, day=1).year,
                                            datetime.datetime(year=year, month=month, day=1).month)[1]
    return sum_days_in_month


def condition_or_0(condition):
    if condition:
        return float(condition)
    else:
        return 0

def condition_or_0_int(condition):
    if condition:
        return int(condition)
    else:
        return 0

# Запрос прайс-листа по группам
def price_chart(group, wash_id=None):
    price_chart = []
    if wash_id:
        order = Order.objects.get(id=wash_id)
    else:
        order = None
    for price in Price.objects.all().filter(group=group):
        price_dict = dict()
        price_dict['id'] = price.id
        price_dict['name'] = price.name
        if price.description:
            price_dict['description'] = price.description.split(",")
        else:
            price_dict['description'] = None
        price_dict['work_time'] = price.work_time
        price_dict['price_car'] = price.price_car
        price_dict['price_crossover'] = price.price_crossover
        price_dict['price_suv'] = price.price_suv
        price_dict['comment'] = price.comment
        if wash_id:
            for i in order.price_ids[:-1].split(','):
                if int(i) == price.id:
                    price_dict['checked'] = True
        price_chart.append(price_dict)
    return price_chart


# Последние заказы мойки
def order_parade(order_date=None, lenght=None, wash_id=None, car_id=None, in_year=None, in_month=None, park_car=None,
                 car_number=None):
    # Чарт с заказами
    order_chart = []
    if order_date:
        Orders = Order.objects.all().filter(dt=order_date)
    else:
        Orders = Order.objects.all().order_by('-dt')

    if car_id:
        Orders = Order.objects.all().filter(dt__range=(datetime.datetime(year=in_year, month=in_month, day=1),
                                                       datetime.datetime(year=in_year, month=in_month,
                                                                         day=last_day_of_month(in_year, in_month),
                                                                         hour=23, minute=59, second=59,
                                                                         microsecond=999999))).filter(car_id=car_id)

    if in_year and in_month and park_car:
        Orders = Order.objects.all().filter(dt__range=(datetime.datetime(year=in_year, month=in_month, day=1),
                                                       datetime.datetime(year=in_year, month=in_month,
                                                                         day=last_day_of_month(in_year, in_month),
                                                                         hour=23, minute=59, second=59,
                                                                         microsecond=999999))).filter(park_car=park_car)

    if car_number:
        Orders = Order.objects.all().filter(dt__range=(datetime.datetime(year=in_year, month=in_month, day=1),
                                                       datetime.datetime(year=in_year, month=in_month,
                                                                         day=last_day_of_month(in_year, in_month),
                                                                         hour=23, minute=59, second=59,
                                                                         microsecond=999999))).filter(
            car_number=car_number)

    if in_year and in_month and car_number is False:
        Orders = Order.objects.all().filter(dt__range=(datetime.datetime(year=in_year, month=in_month, day=1),
                                                       datetime.datetime(year=in_year, month=in_month,
                                                                         day=last_day_of_month(in_year, in_month),
                                                                         hour=23, minute=59, second=59,
                                                                         microsecond=999999))).filter(park_car=False)

    for order in Orders:
        order_dict = dict()
        order_dict['id'] = order.id
        order_dict['dt'] = order.dt
        if order.car_id:
            order_dict['num'] = Cars.objects.using('Cx_TaxiConfiguration').get(id=order.car_id).number.replace(' ', '')
        elif order.car_number:
            order_dict['num'] = order.car_number
        else:
            order_dict['num'] = 'Без номера'
        service_list = list()
        for i in order.price_ids.split(',')[:len(order.price_ids.split(',')) - 1]:
            service_list.append(Price.objects.get(id=i).name)
        order_dict['service_list'] = service_list
        order_dict['add_service'] = order.add_service
        order_dict['pay_type'] = order.pay_type
        order_dict['comment'] = order.comment
        order_dict['sum'] = order.sum
        order_dict['sum_time'] = order.sum_time
        if order.park_car:
            order_dict['park'] = True
        if order.car_type == "Cars":
            order_dict['car_type'] = "Легков"
        elif order.car_type == "Crossover":
            order_dict['car_type'] = "Кроссов"
        elif order.car_type == "SUV":
            order_dict['car_type'] = "Внедорож"
        if wash_id == order.id:
            order_dict['selected'] = True
        order_chart.append(order_dict)
    if lenght:
        return order_chart[:lenght]
    else:
        return order_chart


# Заказы на текущий день
def today_parade(wash_id=None):
    current_day = datetime.datetime.today()
    twenty_minutes = timedelta(minutes=20)
    today_current_smena = current_day.replace(hour=8, minute=00, second=00, microsecond=0)
    today_smena_end = current_day.replace(hour=20, minute=40, second=00, microsecond=0)

    sum_previous_order_time = 0
    today_chart = []
    while today_current_smena <= today_smena_end:
        today_dict = dict()
        if wash_id:
            current_order = order_parade(order_date=today_current_smena, wash_id=wash_id)
        else:
            current_order = order_parade(order_date=today_current_smena)
        today_dict['time'] = today_current_smena
        # print(len(today_chart))

        if current_order:
            sum_previous_order_time = 0
            today_dict['id'] = current_order[0]['id']
            today_dict['dt'] = current_order[0]['dt']
            today_dict['num'] = current_order[0]['num']
            today_dict['service_list'] = current_order[0]['service_list']
            today_dict['add_service'] = current_order[0]['add_service']
            today_dict['pay_type'] = current_order[0]['pay_type']
            today_dict['comment'] = current_order[0]['comment']
            today_dict['sum'] = current_order[0]['sum']
            today_dict['sum_time'] = current_order[0]['sum_time']
            sum_previous_order_time += current_order[0]['sum_time']
            try:
                if current_order[0]['park']:
                    today_dict['park'] = True
            except:
                today_dict['park'] = False
            today_dict['car_type'] = current_order[0]['car_type']
            try:
                if current_order[0]['selected']:
                    today_dict['selected'] = True
            except:
                today_dict['selected'] = False
        if Order.objects.all().filter(
                dt__range=(today_current_smena - timedelta(minutes=int(sum_previous_order_time)) + timedelta(seconds=1),
                           today_current_smena)):
            today_dict['block_time'] = True
        today_current_smena += twenty_minutes
        today_chart.append(today_dict)
    return today_chart


# ------------------------- ГЛАВНАЯ СТРАНИЦА МОЙКА ----------------------


def order(request):
    # Инициируем заново переменные с временем, т.к. нужно актуальное время
    current_day = datetime.datetime.today()
    day_pus_one = timedelta(days=1)

    cars = Cars.objects.using('Cx_TaxiConfiguration').all()

    if Order.objects.last() is None:
        last_order_id = 0
    else:
        last_order_id = Order.objects.last().id

    if request.method == 'POST':
        order_form = OrderForm(request.POST)
        if order_form.is_valid():
            post = order_form.save(commit=False)
            post.dt = request.POST.get('order_time')
            post.car_number = request.POST.get('car_number')
            post.car_id = request.POST.get('car_id')
            post.car_type = request.POST.get('car_type')
            post.price_ids = request.POST.get('price_ids')
            post.sum = request.POST.get('sum')
            post.sum_time = request.POST.get('sum_time')
            post.add_service = request.POST.get('add_service')
            post.add_price = request.POST.get('add_price')
            post.pay_type = request.POST.get('pay_type')
            post.comment = request.POST.get('comment')
            if request.POST.get('park_car'):
                post.park_car = True
            post.save()
        return HttpResponseRedirect('/wash')

    context = {'price_chart_main': price_chart(1),
               'price_chart_complex': price_chart(2),
               'price_chart_additional': price_chart(3),
               'cars': cars.order_by('callsign'),
               'last_order_id': last_order_id,
               'current_day': current_day,
               'order_chart': order_parade(lenght=30),
               'today_chart': today_parade()}

    return render(request, 'order.html', context)


def order_update(request, wash_id):
    current_day = datetime.datetime.today()
    order = get_object_or_404(Order, id=wash_id)
    cars = Cars.objects.using('Cx_TaxiConfiguration').all()

    if order.park_car:
        try:
            car = Cars.objects.using('Cx_TaxiConfiguration').get(id=order.car_id)
            order.car_number = car.number
            order.car_id = car.id
        except:
            order.car_number = "Без номера"
            # order.car_id = None

    if request.method == 'POST':
        order_form = OrderForm(request.POST, instance=order)
        if order_form.is_valid():
            post = order_form.save(commit=False)
            post.dt = request.POST.get('order_time')
            post.car_number = request.POST.get('car_number')
            post.car_id = request.POST.get('car_id')
            post.car_type = request.POST.get('car_type')
            post.price_ids = request.POST.get('price_ids')
            post.sum = request.POST.get('sum')
            post.sum_time = request.POST.get('sum_time')
            post.add_service = request.POST.get('add_service')
            post.add_price = request.POST.get('add_price')
            post.pay_type = request.POST.get('pay_type')
            post.comment = request.POST.get('comment')
            if request.POST.get('park_car'):
                post.park_car = True
            post.save()
        return HttpResponseRedirect('/wash')

    context = {'price_chart_main': price_chart(1, wash_id),
               'price_chart_complex': price_chart(2, wash_id),
               'price_chart_additional': price_chart(3, wash_id),
               'cars': cars.order_by('callsign'),
               'current_day': current_day,
               'today_chart': today_parade(wash_id=wash_id),
               'order': order}
    return render(request, 'order.html', context)


def order_delete(request, wash_id):
    order = get_object_or_404(Order, id=wash_id)
    order.delete()
    return HttpResponseRedirect('/wash')


# ------------------------- ПРАЙС-ЛИСТ МОЙКА ----------------------

def price(request):
    # Инициируем заново переменные с временем, т.к. нужно актуальное время
    current_day = datetime.datetime.today()

    if request.method == 'POST':
        price_form = PriceForm(request.POST)
        if price_form.is_valid():
            post = price_form.save(commit=False)
            post.name = request.POST.get('name')
            post.description = request.POST.get('description')
            post.price_car = request.POST.get('price_car')
            post.price_crossover = request.POST.get('price_crossover')
            post.price_suv = request.POST.get('price_suv')
            post.work_time = request.POST.get('work_time')
            post.comment = request.POST.get('comment')
            post.group = request.POST.get('group')
            post.save()
        return HttpResponseRedirect('/wash/price')

    context = {'price_chart_main': price_chart(1),
               'price_chart_complex': price_chart(2),
               'price_chart_additional': price_chart(3),
               }
    return render(request, 'price.html', context)


# ------------------------- ОТЧЕТЫ ----------------------

# ----------- ОТЧЕТ "ПАРК" ---------------
def report_park(request, in_year=datetime.datetime.now().year, in_month=datetime.datetime.now().month, in_car_id=None):
    # !!!! ЧАРТ С МЕСЯЦАМИ И ГОДАМИ !!!!
    current_day = datetime.datetime.now()
    date_chart = []
    for year in range(current_day.year, 2018, -1):
        for month in range(12, 0, -1):
            date_dict = dict()
            if year == current_day.year and month > current_day.month:
                continue
            if year == in_year and month == in_month:
                date_dict['current_month'] = True
            date_dict['year'] = year
            date_dict['month'] = datetime.datetime(year=year, month=month, day=1)
            orders_request = Order.objects.all().filter(dt__range=(datetime.datetime(year=year, month=month, day=1),
                                                                   datetime.datetime(year=year, month=month,
                                                                                     day=last_day_of_month(year, month),
                                                                                     hour=23, minute=59, second=59,
                                                                                     microsecond=999999)))
            all_park_money = condition_or_0(orders_request.filter(park_car=True).aggregate(Sum('sum'))['sum__sum'])
            date_dict['all_park_money'] = '{0:,}'.format(all_park_money).replace(',', ' ')
            all_park_orders = orders_request.filter(park_car=True).count()
            date_dict['all_park_orders'] = '{0:,}'.format(all_park_orders).replace(',', ' ')
            date_chart.append(date_dict)
    # !!!! КОНЕЦ ЧАРТ С МЕСЯЦАМИ И ГОДАМИ !!!!

    # !!! Начало ЧАРТ С ПАРКОВЫМИ АВТО
    park_chart = Order.objects.all().filter(dt__range=(datetime.datetime(year=in_year, month=in_month, day=1),
                                                       datetime.datetime(year=in_year, month=in_month,
                                                                         day=last_day_of_month(in_year, in_month),
                                                                         hour=23, minute=59, second=59,
                                                                         microsecond=999999))).filter(
        park_car=True).values('car_id').annotate(count=Count('car_id')).annotate(sum=Sum('sum'))

    # !!! Конец ЧАРТ С ПАРКОВЫМИ АВТО
    # Добавляем к тачкам номера
    for car in park_chart:
        try:
            Cars_query = Cars.objects.using('Cx_TaxiConfiguration').get(id=car['car_id'])
            car['car_number'] = Cars_query.number
            car['callsign'] = Cars_query.callsign
            if int(car['car_id']) == in_car_id:
                car['current_car'] = True
        except:
            car['car_number'] = None

    # !!! Начало ЧАРТ С ВЫБРАННЫМ АВТО
    if in_car_id:
        order_chart = order_parade(car_id=in_car_id, in_year=in_year, in_month=in_month)
    else:
        order_chart = order_parade(in_year=in_year, in_month=in_month, park_car=True)

    # !!! Конец ЧАРТ С ВЫБРАННЫМ АВТО

    context = {'in_year': in_year,
               'in_month': in_month,
               'date_chart': date_chart,
               'park_chart': park_chart,
               'order_chart': order_chart,
               'in_car_id': in_car_id,
               'report_park_marker': True
               }
    return render(request, 'report_park.html', context)


# /----------- ОТЧЕТ "ПАРК" ---------------


# ----------- ОТЧЕТ "С УЛИЦЫ" ---------------
def report_enemy(request, in_year=datetime.datetime.now().year, in_month=datetime.datetime.now().month,
                 car_number=None):
    # !!!! ЧАРТ С МЕСЯЦАМИ И ГОДАМИ !!!!
    current_day = datetime.datetime.now()
    date_chart = []
    for year in range(current_day.year, 2018, -1):
        for month in range(12, 0, -1):
            date_dict = dict()
            if year == current_day.year and month > current_day.month:
                continue
            if year == in_year and month == in_month:
                date_dict['current_month'] = True
            date_dict['year'] = year
            date_dict['month'] = datetime.datetime(year=year, month=month, day=1)
            orders_request = Order.objects.all().filter(dt__range=(datetime.datetime(year=year, month=month, day=1),
                                                                   datetime.datetime(year=year, month=month,
                                                                                     day=last_day_of_month(year, month),
                                                                                     hour=23, minute=59, second=59,
                                                                                     microsecond=999999)))
            all_enemy_money = condition_or_0(orders_request.filter(park_car=False).aggregate(Sum('sum'))['sum__sum'])
            date_dict['all_park_money'] = '{0:,}'.format(all_enemy_money).replace(',', ' ')
            all_enemy_orders = orders_request.filter(park_car=False).count()
            date_dict['all_park_orders'] = '{0:,}'.format(all_enemy_orders).replace(',', ' ')
            date_chart.append(date_dict)
    # !!!! КОНЕЦ ЧАРТ С МЕСЯЦАМИ И ГОДАМИ !!!!

    # !!! Начало ЧАРТ АВТО
    enemy_chart = Order.objects.all().filter(dt__range=(datetime.datetime(year=in_year, month=in_month, day=1),
                                                        datetime.datetime(year=in_year, month=in_month,
                                                                          day=last_day_of_month(in_year, in_month),
                                                                          hour=23, minute=59, second=59,
                                                                          microsecond=999999))).filter(
        park_car=False).values('car_number', 'car_type').annotate(count=Count('car_number')).annotate(sum=Sum('sum'))

    # Добавляем тип авто
    for car in enemy_chart:
        if car['car_type'] == 'Cars':
            car['car_type_description'] = 'Легковая'
        if car['car_type'] == 'Crossover':
            car['car_type_description'] = 'Кроссовер'
        if car['car_type'] == 'SUV':
            car['car_type_description'] = 'Внедорожник'
        if car['car_number'] == car_number:
            car['current_car'] = True
    # !!! Конец ЧАРТ С АВТО

    # !!! Начало ЧАРТ С ВЫБРАННЫМ АВТО
    if car_number:
        order_chart = order_parade(car_number=car_number, in_year=in_year, in_month=in_month)
    else:
        order_chart = order_parade(in_year=in_year, in_month=in_month, car_number=False)

    # !!! Конец ЧАРТ С ВЫБРАННЫМ АВТО

    context = {'in_year': in_year,
               'in_month': in_month,
               'date_chart': date_chart,
               'park_chart': enemy_chart,
               'order_chart': order_chart,
               'car_number': car_number,
               'report_enemy_marker': True
               }
    return render(request, 'report_enemy.html', context)


# /----------- ОТЧЕТ "С УЛИЦЫ" ---------------


# ----------- ОТЧЕТ "ИТОГОВЫЙ" ---------------
def report_all(request, in_year=datetime.datetime.now().year, in_month=datetime.datetime.now().month):
    # Форматирование разрядности
    def bit_depth(value):
        return '{0:,}'.format(value).replace(',', ' ')

    # --- ЧАРТ ИТОГИ ЗАКАЗЫ - РУБ ---
    current_day = datetime.datetime.now()
    date_chart = []
    for year in range(current_day.year, 2018, -1):
        for month in range(12, 0, -1):
            date_dict = dict()
            if year == current_day.year and month > current_day.month:
                continue
            if year == in_year and month == in_month:
                date_dict['current_month'] = True
            date_dict['year'] = year
            date_dict['month'] = datetime.datetime(year=year, month=month, day=1)
            orders_request = Order.objects.all().filter(dt__range=(datetime.datetime(year=year, month=month, day=1),
                                                                   datetime.datetime(year=year, month=month,
                                                                                     day=last_day_of_month(year, month),
                                                                                     hour=23, minute=59, second=59,
                                                                                     microsecond=999999)))
            date_dict['all_money'] = bit_depth(condition_or_0(orders_request.aggregate(Sum('sum'))['sum__sum']))
            date_dict['all_orders'] = bit_depth(orders_request.count())
            date_dict['all_park_money'] = bit_depth(
                condition_or_0(orders_request.filter(park_car=True).aggregate(Sum('sum'))['sum__sum']))
            date_dict['all_park_orders'] = bit_depth(orders_request.filter(park_car=True).count())
            date_dict['all_enemy_money'] = bit_depth(
                condition_or_0(orders_request.filter(park_car=False).aggregate(Sum('sum'))['sum__sum']))
            date_dict['all_enemy_orders'] = bit_depth(orders_request.filter(park_car=False).count())
            date_chart.append(date_dict)
        # --- / ЧАРТ ИТОГИ ЗАКАЗЫ - РУБ ---

    orders_request = Order.objects.all().filter(dt__range=(datetime.datetime(year=in_year, month=in_month, day=1),
                                                           datetime.datetime(year=in_year, month=in_month,
                                                                             day=last_day_of_month(in_year, in_month),
                                                                             hour=23, minute=59, second=59,
                                                                             microsecond=999999)))

    # --- ЧАРТ ИТОГИ УСЛУГИ ---
    prices_id_request = Price.objects.all()
    # Улица
    price_id_chart_street = []
    for price_id in prices_id_request:
        price_id_dict = dict()
        count = 0
        for order in orders_request.filter(price_ids__contains=price_id.id).filter(park_car=False):
            for i in order.price_ids.split(',')[:len(order.price_ids.split(',')) - 1]:
                if i == str(price_id.id):
                    count += 1
            price_id_dict['count'] = count
            if order.car_type == 'Cars':
                price_id_dict['sum'] = price_id.price_car * count
            if order.car_type == 'Crossover':
                price_id_dict['sum'] = price_id.price_crossover * count
            if order.car_type == 'SUV':
                price_id_dict['sum'] = price_id.price_suv * count
        price_id_dict['name'] = price_id.name
        # Чтобы выкинуть пустые значения
        try:
            price_id_dict['count']
        except:
            continue
        # /Чтобы выкинуть пустые значения
        price_id_chart_street.append(price_id_dict)
    # Парк
    price_id_chart_park = []
    for price_id in prices_id_request:
        price_id_dict = dict()
        count = 0
        for order in orders_request.filter(price_ids__contains=price_id.id).filter(park_car=True):
            for i in order.price_ids.split(',')[:len(order.price_ids.split(',')) - 1]:
                if i == str(price_id.id):
                    count += 1
            price_id_dict['count'] = count
            if order.car_type == 'Cars':
                price_id_dict['sum'] = price_id.price_car * count
            if order.car_type == 'Crossover':
                price_id_dict['sum'] = price_id.price_crossover * count
            if order.car_type == 'SUV':
                price_id_dict['sum'] = price_id.price_suv * count
        price_id_dict['name'] = price_id.name
        # Чтобы выкинуть пустые значения
        try:
            price_id_dict['count']
        except:
            continue
        # /Чтобы выкинуть пустые значения
        price_id_chart_park.append(price_id_dict)
    # --- / ЧАРТ ИТОГИ УСЛУГИ ---

    # --- ЧАРТ ТИПЫ ОПЛАТЫ ---
    # Улица
    street_cash_cnt = orders_request.filter(park_car=False, pay_type='cash').count()
    street_cash_rub = condition_or_0_int(orders_request.filter(park_car=False, pay_type='cash').aggregate(Sum('sum'))['sum__sum'])
    street_terminal_cnt = orders_request.filter(park_car=False, pay_type='terminal').count()
    street_terminal_rub = condition_or_0_int(orders_request.filter(park_car=False, pay_type='terminal').aggregate(Sum('sum'))['sum__sum'])
    street_bnal_cnt = orders_request.filter(park_car=False, pay_type='bnal').count()
    street_bnal_rub = condition_or_0_int(orders_request.filter(park_car=False, pay_type='bnal').aggregate(Sum('sum'))['sum__sum'])
    street_park_cnt = orders_request.filter(park_car=False, pay_type='park').count()
    street_park_rub = condition_or_0_int(orders_request.filter(park_car=False, pay_type='park').aggregate(Sum('sum'))['sum__sum'])
    # Парк
    park_cash_cnt = orders_request.filter(park_car=True, pay_type='cash').count()
    park_cash_rub = condition_or_0_int(orders_request.filter(park_car=True, pay_type='cash').aggregate(Sum('sum'))['sum__sum'])
    park_terminal_cnt = orders_request.filter(park_car=True, pay_type='terminal').count()
    park_terminal_rub = condition_or_0_int(orders_request.filter(park_car=True, pay_type='terminal').aggregate(Sum('sum'))['sum__sum'])
    park_bnal_cnt = orders_request.filter(park_car=True, pay_type='bnal').count()
    park_bnal_rub = condition_or_0_int(orders_request.filter(park_car=True, pay_type='bnal').aggregate(Sum('sum'))['sum__sum'])
    park_park_cnt = orders_request.filter(park_car=True, pay_type='park').count()
    park_park_rub = condition_or_0_int(orders_request.filter(park_car=True, pay_type='park').aggregate(Sum('sum'))['sum__sum'])
    # --- /ЧАРТ ТИПЫ ОПЛАТЫ ---

    context = {'in_year': in_year,
               'in_month': in_month,
               'date_chart': date_chart,
               'price_id_chart_street': price_id_chart_street,
               'price_id_chart_park': price_id_chart_park,
               'street_cash_cnt': street_cash_cnt,
               'street_cash_rub': street_cash_rub,
               'street_terminal_cnt': street_terminal_cnt,
               'street_terminal_rub': street_terminal_rub,
               'street_bnal_cnt': street_bnal_cnt,
               'street_bnal_rub': street_bnal_rub,
               'street_park_cnt': street_park_cnt,
               'street_park_rub': street_park_rub,
               'park_cash_cnt': park_cash_cnt,
               'park_cash_rub': park_cash_rub,
               'park_terminal_cnt': park_terminal_cnt,
               'park_terminal_rub': park_terminal_rub,
               'park_bnal_cnt': park_bnal_cnt,
               'park_bnal_rub': park_bnal_rub,
               'park_park_cnt': park_park_cnt,
               'park_park_rub': park_park_rub,
               'report_all_marker': True
               }
    return render(request, 'report_all.html', context)

# /----------- ОТЧЕТ "ИТОГОВЫЙ" ---------------
