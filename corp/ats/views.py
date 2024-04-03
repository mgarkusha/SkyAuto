import calendar
import datetime
from datetime import timedelta

from django.contrib import auth
from django.http import Http404
from django.shortcuts import render, HttpResponseRedirect
from infinity.models import Drivers, Cars, Corporations, Clientcontacts

from .models import FSms


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


def strfdelta(tdelta):
    d = {"days": tdelta.days}
    d["hours"], rem = divmod(tdelta.seconds, 3600)
    d["minutes"], d["seconds"] = divmod(rem, 60)
    if tdelta.days == 0:
        return '{hours} часа {minutes} минут'.format(**d)
    else:
        return '{days} дней {hours} часа {minutes} минут'.format(**d)


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


# Сырое подключение к PgSQL
# con_conf = psycopg2.connect(dbname="Cx_TaxiConfiguration", user="cxdbuser", host="127.0.0.1", port="10000", password="cxdbwizard")
# cursor_conf = con_conf.cursor()
# cursor_conf.execute("""select * from \"public\".\"ClientContacts\" where \"ClientContacts\".\"Contact\" like '%79219520332%';""")
# rows = cursor_conf.fetchall()
# print(rows)

# ------ КОНЕЦ ОБЩИЕ ПЕРЕМЕННЫЕ И ФУНКЦИИ -----------

def sms(request, in_year=None, in_month=None, in_day=None):
    if in_year:
        current_day = datetime.datetime(year=in_year, month=in_month, day=in_day, hour=0, minute=0, second=0,
                                        microsecond=0)
    else:
        current_day = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
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
        sms_dict['errorcode'] = sms_errorcode(i.errorcode)
        sms_chart.append(sms_dict)

    day_chart = []
    day_count = 30
    for single_date in (datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(n) for n
                        in
                        range(day_count)):
        day_dict = dict()
        day_dict['date'] = single_date.replace(hour=0, minute=0, second=0, microsecond=0)
        day_dict['cnt'] = FSms.objects.using('fb').filter(datetime_d=str(single_date - start_day).split()[0]).count()
        if single_date == current_day:
            day_dict['current_day'] = True
        day_chart.append(day_dict)

    # cars = Cars.objects.using('Cx_TaxiConfiguration')

    context = {'sms_chart': sms_chart,
               'day_chart': day_chart}
    return render(request, 'sms.html', context)
