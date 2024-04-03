from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from infinity.models import Drivers, Cars


class Gibdd(models.Model):
    date = models.DateTimeField(auto_now_add=True, verbose_name='Дата документа')
    incident_date = models.DateTimeField(verbose_name='Дата нарушения')
    incident_number = models.CharField(unique=True, max_length=20, default=0, verbose_name='Номер постановления')
    incident_decree_date = models.DateTimeField(verbose_name='Дата постановления')
    incident_type = models.CharField(default=0, max_length=500, verbose_name='Суть нарушения')
    incident_speed = models.CharField(default=0, max_length=10, verbose_name='Скорость движения')
    incident_place = models.CharField(verbose_name='Место нарушения', max_length=500)
    penalty_gibdd = models.DecimalField(max_digits=6, decimal_places=0, default=0, verbose_name='Сумма штрафа ГИБДД')
    driver_id = models.CharField(verbose_name='id Водителя', max_length=12)  # id водилы в базе инфинити
    car_id = models.CharField(verbose_name='id Машины', max_length=12)  # id тачки в базе инфинити
    speed_recommend = models.CharField(default=0, max_length=10, verbose_name='Разрешенная скорость движения')
    penalty_company = models.DecimalField(max_digits=6, decimal_places=0, default=0, verbose_name='Сумма штрафа')
    manager_comment = models.CharField(verbose_name='Комментарий руководителя', max_length=500)
    penalty_gibdd_paid = models.BooleanField(verbose_name='Оплата штрафа в ГИБДД', default=False)
    penalty_gibdd_paid_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата оплаты штрафа в ГИБДД')
    penalty_driver_paid = models.BooleanField(verbose_name='Оплата штрафа водителем', default=False)
    penalty_driver_paid_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата оплаты штрафа водителем')

    def get_driver_name(self):
        driver = Drivers.objects.using('Cx_TaxiConfiguration').get(id=self.driver_id)
        return driver.fullname

    def get_car_number(self):
        car = Cars.objects.using('Cx_TaxiConfiguration').get(id=self.car_id)
        return car.number


class CompanyPenalty(models.Model):
    date = models.DateTimeField(auto_now_add=True, verbose_name='Дата документа')  # +
    incident_date = models.DateTimeField(verbose_name='Дата нарушения')  # +
    incident_type = models.CharField(default=0, max_length=500, verbose_name='Суть нарушения')  # +
    incident_speed = models.CharField(default=0, max_length=10, verbose_name='Скорость движения')  # +
    incident_place = models.CharField(verbose_name='Место нарушения', max_length=500)  # +
    driver_id = models.CharField(verbose_name='id Водителя', max_length=12)  # id водилы в базе инфинити +
    car_id = models.CharField(verbose_name='id Машины', max_length=12)  # id тачки в базе инфинити +
    speed_recommend = models.CharField(default=0, max_length=10, verbose_name='Разрешенная скорость движения')  # +
    penalty_company = models.DecimalField(max_digits=6, decimal_places=0, default=0, verbose_name='Сумма штрафа')  # +
    manager_comment = models.CharField(verbose_name='Комментарий руководителя', max_length=500)  # +
    penalty_driver_paid = models.BooleanField(verbose_name='Оплата штрафа водителем', default=False)  # +
    penalty_driver_paid_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата оплаты штрафа водителем')  # +

    def get_driver_name(self):
        driver = Drivers.objects.using('Cx_TaxiConfiguration').get(id=self.driver_id)
        return driver.fullname

    def get_car_number(self):
        car = Cars.objects.using('Cx_TaxiConfiguration').get(id=self.car_id)
        return car.number
