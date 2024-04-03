from django.db import models
from django.contrib.auth.models import User
from infinity.models import Drivers, Cars


class ComplaintStatus(models.Model):
    complaint_status_text = models.CharField(verbose_name='Стус жалобы', max_length=32)

    def __str__(self):
        return self.complaint_status_text


class Complaint(models.Model):
    complaint_number = models.DecimalField(max_digits=5, decimal_places=0, verbose_name='Номер жалобы')
    complaint_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата подачи жалобы')
    complaint_date_close = models.DateTimeField(blank=True, null=True, verbose_name='Дата рассмотрения')
    operator_name = models.CharField(verbose_name='Диспетчер', max_length=100)
    # operator_name = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Диспетчер')
    driver_id = models.CharField(verbose_name='ФИО Водителя', max_length=12)  # id водилы в базе инфинити
    car_id = models.CharField(verbose_name='Номер машины', max_length=12)  # id тачки в базе инфинити
    complaint_text = models.TextField(verbose_name='Текст жалобы', max_length=500)
    complaint_status = models.ForeignKey(ComplaintStatus, on_delete=models.CASCADE, verbose_name='Статус жалобы')
    complaint_answer = models.CharField(verbose_name='Ответ руководителя', max_length=500)
    complaint_penalty = models.DecimalField(max_digits=6, decimal_places=0, default=0, verbose_name='Сумма штрафа')
    complaint_archive = models.BooleanField(verbose_name='Архив', default=False)

    def get_driver_name(self):
        driver = Drivers.objects.using('Cx_TaxiConfiguration').get(id=self.driver_id)
        return driver.fullname

    def get_car_number(self):
        car = Cars.objects.using('Cx_TaxiConfiguration').get(id=self.car_id)
        return car.number
