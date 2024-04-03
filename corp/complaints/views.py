from django.shortcuts import render, render_to_response, get_object_or_404, HttpResponseRedirect
from .models import Complaint, ComplaintStatus
from infinity.models import Cars, Drivers
from salary.models import Salary
from .forms import ComplaintForm, ComplaintManagerForm
from django.contrib import auth
from django.db.models import Sum, Count, Min, Max
import datetime
import calendar
import operator
from django.http import Http404
from django.core.mail import send_mail
from django.conf import settings


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
            return render(request, 'complaint_rd.html', {'errors': True})
    raise Http404


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/')


def condition_or_0(condition):
    if condition:
        return int(condition)
    else:
        return 0


# ------ НАЧАЛО ОБЩИЕ ПЕРЕМЕННЫЕ И ФУНКЦИИ -----------


# Определяем водителей "на линии". Если сидит в машине, значит online
def driver_online(diver_id):
    cars = Cars.objects.using('Cx_TaxiConfiguration').filter(idcurrentdriver=diver_id)
    if cars:
        driver_status = 1
    else:
        driver_status = 0
    return driver_status


# Список id водителей, на которых есть жалобы в заданный месяц
def driver_list_complaints_id(month):
    id = set(list(
        [int(i['driver_id']) for i in Complaint.objects.filter(complaint_date__month=month).values('driver_id')]))
    return id


# Список id неработающих водителей из таблицы водителей (isblocked=1, isdeleted=1)
def driver_list_work_id():
    id = list([int(i['id']) for i in
               Drivers.objects.using('Cx_TaxiConfiguration').filter(isblocked=1).values('id')])
    return id


# Список водителей, отключенных  от показа (Гаркуша)
driver_list_my_block = [5018737745]
driver_list_my_block_names = []
for id in driver_list_my_block:
    name = Drivers.objects.using('Cx_TaxiConfiguration').get(id=id).fullname
    driver_list_my_block_names.append(name)


# Статус жалобы РУС
def complaint_status_rus(status_id):
    result = 'Не известно'
    if status_id == 1:
        result = 'Подана'
    elif status_id == 2:
        result = 'Рассмотрение'
    elif status_id == 3:
        result = 'Закрыта'
    return result


# ------ КОНЕЦ ОБЩИЕ ПЕРЕМЕННЫЕ И ФУНКЦИИ -----------


def index(request, in_month=None, in_driver_id=None):
    def add_months(sourcedate, months):
        month = sourcedate.month - 1 + months
        year = sourcedate.year + month // 12
        month = month % 12 + 1
        day = min(sourcedate.day, calendar.monthrange(year, month)[1])
        return datetime.date(year, month, day)

    # Если Архив
    if in_driver_id:
        complaint_filter = True
        filter_driver_name = Drivers.objects.using('Cx_TaxiConfiguration').get(id=in_driver_id)
        filter_month_name = datetime.datetime.now().replace(month=int(in_month))
    else:
        complaint_filter = False
        filter_driver_name = None
        filter_month_name = None
    # /Если Архив

    complaint_all = Complaint.objects.all()

    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! С годом тут пока тяп-ляп =(
    def get_complaint(driver_id, month):
        complaint = Complaint.objects.filter(driver_id=driver_id).filter(
            complaint_date__month=month, complaint_date__year=datetime.date.today().year)
        return complaint

    def driver_chart_month(month):
        driver_chart = []
        for driver_id in driver_list_complaints_id(month):
            driver_dict = dict()
            driver_dict['fullname'] = Drivers.objects.using('Cx_TaxiConfiguration').get(id=driver_id).fullname
            driver_dict['complaint_date'] = month
            driver_dict['driver_id'] = driver_id
            driver_dict['complaints_count_sent'] = condition_or_0(
                get_complaint(driver_id, month).filter(complaint_status__in=[1, 2]).count())
            driver_dict['complaints_count_closed'] = condition_or_0(
                get_complaint(driver_id, month).filter(complaint_status=3).count())
            driver_dict['complaints_count_all'] = condition_or_0(get_complaint(driver_id, month).count())
            driver_dict['complaint_filter'] = True if in_driver_id == driver_id and month == in_month else False
            driver_chart.append(driver_dict)
        # Сортируем по fullname
        sort_fullname_chart = []
        for i in sorted(driver_chart, key=operator.itemgetter("fullname")):
            sort_fullname_chart.append(i)
        return sort_fullname_chart

    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! С годом тут пока тяп-ляп =(
    if in_driver_id:
        complaint_rd = complaint_all.filter(driver_id=in_driver_id).filter(complaint_date__month=in_month).order_by(
            'complaint_date').reverse()
    else:
        complaint_rd = complaint_all.filter(complaint_archive=False).exclude(
            driver_id__in=driver_list_work_id()).order_by('complaint_date').reverse()

    context = {'complaint_rd': complaint_rd, 'driver_chart': driver_chart_month(datetime.date.today().month),
               'driver_chart_previous_month': driver_chart_month(add_months(datetime.date.today(), -1).month),
               'username': auth.get_user(request).username,
               'current_month': datetime.date.today(),
               'previous_month': add_months(datetime.date.today(), -1),
               'count_current_month': complaint_all.filter(complaint_date__month=datetime.date.today().month).count(),
               'count_previous_month': complaint_all.filter(
                   complaint_date__month=add_months(datetime.date.today(), -1).month).count(),
               'menu_complaint_active': True,
               'complaint_filter': complaint_filter,
               'filter_driver_name': filter_driver_name,
               'filter_month_name': filter_month_name}
    return render(request, 'complaint_rd.html', context)


def complaint_view_archive(request):
    complaint_rd = Complaint.objects.all().filter(complaint_archive=True).order_by('complaint_date_close').reverse()
    return render(request, 'complaint_rd.html',
                  {'complaint_rd': complaint_rd, 'archive_active': True})


def complaint_create(request):
    if request.method == 'POST':
        form = ComplaintForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.complaint_number = Complaint.objects.count() + 1
            post.complaint_date = datetime.date.today()
            post.complaint_status = ComplaintStatus.objects.get(id=1)  # Новый статус жалобы = Подана на рассмотрение
            if request.user.is_authenticated:
                post.operator_name = request.user.get_full_name()
            else:
                post.operator_name = 'Диспетчер'
            post.complaint_answer = ''
            post.driver_id = request.POST.get('driver_id')
            post.car_id = request.POST.get('car_id')
            post.save()

            # Отправка письма с жалобой!
            def send_my_mail():
                car = Cars.objects.using('Cx_TaxiConfiguration').get(id=post.car_id)
                title = 'Жалоба на водителя: ' + Drivers.objects.using('Cx_TaxiConfiguration').get(
                    id=post.driver_id).fullname + ' №' + str(post.complaint_number) + ' от ' + str(
                    post.complaint_date.strftime("%d %B %Y"))
                message = ''
                html_message = 'Дата и время жалобы: <b>' + str(post.complaint_date.strftime(
                    "%d %B %Y %H:%M:%S")) + '</b><br><br>Водитель: <b>' + Drivers.objects.using(
                    'Cx_TaxiConfiguration').get(
                    id=post.driver_id).fullname + '</b><br><br>Автомобиль: <b>' + car.idmodel.name + '&nbsp;-&nbsp;' + car.number + '</b><br><br>Текст жалобы: <b>' + request.POST.get(
                    'complaint_text') + '</b>'
                send_mail(title, message, settings.EMAIL_HOST_USER,
                          ['i.simancheva@taxirossiya.ru', 'm.garkusha@taxirossiya.ru'], html_message=html_message)

            send_my_mail()
        return HttpResponseRedirect('/')
    else:
        # Список водителей, отключенных  от показа (Гаркуша)
        driver_list_my_block = [5018737745]
        # Список id работающих водителей из таблицы водителей (isblocked!=1)
        driver_list_work_id = list([int(i['id']) for i in
                                    Drivers.objects.using('Cx_TaxiConfiguration').exclude(isblocked=1).exclude(
                                        isdeleted=1).exclude(id__in=driver_list_my_block).values('id')])
        driver_chart = []
        for driver_id in driver_list_work_id:
            driver_dict = dict()
            driver_dict['id'] = driver_id
            driver_dict['fullname'] = Drivers.objects.using('Cx_TaxiConfiguration').get(id=driver_id).fullname
            cars = Cars.objects.using('Cx_TaxiConfiguration').filter(idcurrentdriver=driver_id)
            if cars:
                driver_dict['online'] = driver_online(driver_id)
                driver_dict['car_id'] = cars[0].id
                driver_dict['callsign'] = cars[0].callsign
                driver_dict['carmodel'] = cars[0].idmodel.name
                driver_dict['number'] = cars[0].number
                driver_dict['color'] = cars[0].idcolor.name
            driver_dict['online_sort'] = False if driver_online(driver_id) else True
            driver_chart.append(driver_dict)
        # Сортируем по fullname + online_sort
        sort_fullname_chart = []
        for i in sorted(driver_chart, key=operator.itemgetter("fullname")):
            sort_fullname_chart.append(i)
        sort_online_chart = []
        for i in sorted(sort_fullname_chart, key=operator.itemgetter("online_sort")):
            sort_online_chart.append(i)
        cars_online_list = []
        cars_online_cart = []
        for car in sort_online_chart:
            cars_dict = dict()
            try:
                if car['car_id']:
                    cars_online_list.append(car['car_id'])
                    cars_dict['id'] = car['car_id']
                    cars_dict['callsign'] = car['callsign']
                    cars_dict['carmodel'] = car['carmodel']
                    cars_dict['number'] = car['number']
                    cars_dict['color'] = car['color']
            except:
                continue
            cars_online_cart.append(cars_dict)
        form = ComplaintForm()
        car_inifnity = Cars.objects.using('Cx_TaxiConfiguration').exclude(id__in=cars_online_list).order_by('callsign')
        complaint_num = Complaint.objects.count() + 1
    context = {'complaint_num': complaint_num, 'time': datetime.date.today(), 'form': form,
               'cars_online_cart': cars_online_cart,
               'car_inifnity': car_inifnity,
               'driver_chart': sort_online_chart}
    return render(request, 'complaint_cu.html', context)


def complaint_archive(request, id):
    complaint = get_object_or_404(Complaint, id=id)
    complaint.complaint_archive = True
    complaint.save()
    return HttpResponseRedirect('/')


def complaint_return(request, id):
    complaint = get_object_or_404(Complaint, id=id)
    complaint.complaint_archive = False
    complaint.save()
    return HttpResponseRedirect('/complaint_view_archive')


def complaint_delete(request, id):
    complaint = get_object_or_404(Complaint, id=id)
    complaint.delete()
    return HttpResponseRedirect('/complaint/stat')


def complaint_update(request, id):
    complaint = get_object_or_404(Complaint, id=id)
    complaint_num = complaint.complaint_number
    time = complaint.complaint_date
    if request.method == 'POST':
        form = ComplaintForm(request.POST, instance=complaint)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/complaint/stat')
        context = {'form': form}
        return render(request, 'complaint_cu.html', context)
    context = {'form': ComplaintForm(instance=complaint), 'complaint_num': complaint_num, 'time': time,
               'update_active': True}
    return render(request, 'complaint_cu.html', context)


def complaint_manager(request, id):
    complaint = get_object_or_404(Complaint, id=id)
    edit_marker = True if complaint.complaint_status_id == 3 else False  # Маркер редактирования закрытой жалобы
    complaint.complaint_status = ComplaintStatus.objects.get(id=2)  # Новый статус жалобы = Рассмотрение
    complaint.complaint_archive = False  # И вынимаем из архива
    complaint.save()
    if request.method == 'POST':
        form = ComplaintManagerForm(request.POST, instance=complaint)
        if form.is_valid():
            form.save()
            complaint.complaint_status = ComplaintStatus.objects.get(id=3)  # Новый статус жалобы = Жалоба Закрыта
            complaint.complaint_date_close = datetime.datetime.now()
            complaint.complaint_archive = True  # И отправляем в архив
            complaint.complaint_answer = request.POST.get('complaint_answer')
            complaint.complaint_penalty = request.POST.get('complaint_penalty')
            complaint.save()
            return HttpResponseRedirect('/complaint/stat')
        context = {'form': form}
        return render(request, 'complaint_manager.html', context)
    context = {'edit_marker': edit_marker,
               'complaint_number': complaint.complaint_number,
               'complaint_date': complaint.complaint_date,
               'operator_name': complaint.operator_name,
               'driver_name': complaint.get_driver_name(),
               'car_number': complaint.get_car_number(),
               'complaint_text': complaint.complaint_text,
               'complaint_penalty': complaint.complaint_penalty,
               'complaint_answer': complaint.complaint_answer}
    return render(request, 'complaint_manager.html', context)


def complaint_report(request):
    complaint_all = Complaint.objects.all()
    month_12 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    context = {'complaint_all': complaint_all.distinct(), 'month_12': month_12}
    return render(request, 'complaint_report.html', context)


def driver_stat(request, in_driver_id=None):
    # Список id работающих водителей из таблицы водителей (isblocked!=1)
    driver_list_work_id = list([int(i['id']) for i in
                                Drivers.objects.using('Cx_TaxiConfiguration').exclude(isblocked=1).exclude(
                                    isdeleted=1).exclude(id__in=driver_list_my_block).values('id')])

    def get_complaint(id):
        complaint = Complaint.objects.filter(driver_id=id)
        return complaint

    # ЧАРТ С ВОДИТЕЛЯМИ
    drivers_chart = []
    for driver_id in driver_list_work_id:
        driver_dict = dict()
        driver_dict['driver_id'] = driver_id
        driver_dict['fullname'] = Drivers.objects.using('Cx_TaxiConfiguration').get(id=driver_id).fullname
        driver_dict['complaints_count_sent'] = condition_or_0(
            get_complaint(driver_id).filter(complaint_status__in=[1, 2]).count())
        driver_dict['complaints_count_closed'] = condition_or_0(
            get_complaint(driver_id).filter(complaint_status=3).count())
        driver_dict['complaints_count_all'] = condition_or_0(get_complaint(driver_id).count())
        complaints_count_rub = get_complaint(driver_id).aggregate(Sum('complaint_penalty'))['complaint_penalty__sum']
        if complaints_count_rub:
            driver_dict['complaints_count_rub'] = complaints_count_rub
        else:
            driver_dict['complaints_count_rub'] = 0
        drivers_chart.append(driver_dict)

    sort_fullname_drivers_chart = []
    for i in sorted(drivers_chart, key=operator.itemgetter("fullname")):
        sort_fullname_drivers_chart.append(i)

    sort_drivers_chart = []
    for i in sorted(sort_fullname_drivers_chart, key=operator.itemgetter("complaints_count_sent"), reverse=True):
        sort_drivers_chart.append(i)

    # ЧАРТ С ЖАЛОБАМИ ВОДИТЕЛЯ
    if in_driver_id:
        complaint_driver_all = Complaint.objects.all().filter(driver_id=in_driver_id)
    else:
        complaint_driver_all = Complaint.objects.all().filter(complaint_status_id__in=[1, 2])
    car = Cars.objects.using('Cx_TaxiConfiguration')
    driver_chart = []
    for complaint in complaint_driver_all:
        driver_dict = dict()
        driver_dict['id'] = complaint.id
        driver_dict['complaint_number'] = complaint.complaint_number
        driver_dict['complaint_date'] = complaint.complaint_date
        driver_dict['operator_name'] = complaint.operator_name
        driver_dict['fullname'] = Drivers.objects.using('Cx_TaxiConfiguration').get(id=complaint.driver_id).fullname
        try:
            driver_dict['car_callsign'] = car.get(id=complaint.car_id).callsign
            driver_dict['car_model'] = car.get(id=complaint.car_id).idmodel.name
            driver_dict['car_number'] = car.get(id=complaint.car_id).number
        except:
            driver_dict['car_callsign'] = ''
            driver_dict['car_model'] = 'Нет данных'
            driver_dict['car_number'] = ''
        driver_dict['complaint_text'] = complaint.complaint_text
        driver_dict['complaint_status'] = complaint_status_rus(complaint.complaint_status_id)
        driver_dict['complaint_status_id'] = complaint.complaint_status_id
        driver_dict['complaint_date_close'] = complaint.complaint_date_close
        if complaint.complaint_status_id == 3 and complaint.complaint_penalty == 0:
            driver_dict['complaint_penalty'] = 'Выговор'
        elif complaint.complaint_status_id == 3 and complaint.complaint_penalty > 0:
            driver_dict['complaint_penalty'] = complaint.complaint_penalty
        else:
            driver_dict['complaint_penalty'] = ''
        try:
            salary_payment = Salary.objects.get(driver_id=complaint.driver_id,
                                                salary_year=complaint.complaint_date_close.year,
                                                salary_month=complaint.complaint_date_close.month).payment
            if salary_payment and complaint.complaint_penalty > 0:
                driver_dict['payment_status'] = True
                driver_dict['payment_date'] = datetime.datetime(year=complaint.complaint_date_close.year,
                                                                month=complaint.complaint_date_close.month, day=1)
            elif salary_payment and complaint.complaint_penalty == 0:
                driver_dict['payment_status'] = True
            else:
                driver_dict['payment_status'] = False
        except:
            driver_dict['payment_status'] = False
        try:
            driver_dict['blocked'] = True if Drivers.objects.using('Cx_TaxiConfiguration').get(id=complaint.driver_id,
                                                                                               isblocked=1) else False
        except:
            driver_dict['blocked'] = False
        driver_chart.append(driver_dict)

    sort_date_driver_chart = []
    for i in sorted(driver_chart, key=operator.itemgetter("complaint_date"), reverse=True):
        sort_date_driver_chart.append(i)

    sort_driver_chart = []
    for i in sorted(sort_date_driver_chart, key=operator.itemgetter("blocked")):
        sort_driver_chart.append(i)

    context = {'drivers_chart': sort_drivers_chart,
               'driver_chart': sort_driver_chart,
               'driver_id': in_driver_id,
               'stat_active': True}
    return render(request, 'complaint_stat.html', context)
