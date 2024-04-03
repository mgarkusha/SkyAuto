from django.db import models
from infinity.models import Drivers


class Temporary(models.Model):
    deliverytime = models.DateTimeField(db_column='DeliveryTime')  # Field name made lowercase.
    iddriver = models.BigIntegerField(db_column='IDDriver', blank=True, null=True)  # Field name made lowercase.
    idcorporate = models.BigIntegerField(db_column='IDCorporate', blank=True, null=True)  # Field name made lowercase.
    cost = models.FloatField(db_column='Cost', blank=True, null=True)  # Field name made lowercase.


class Salary(models.Model):
    salary_id = models.DecimalField(max_digits=6, decimal_places=0, default=0, verbose_name='id ЗП = год + мес')
    date = models.DateTimeField(auto_now_add=True, verbose_name='Дата документа')
    driver_id = models.DecimalField(max_digits=10, decimal_places=0, verbose_name='id водителя')
    salary_year = models.DecimalField(max_digits=4, decimal_places=0, verbose_name='Год текущей ЗП')
    salary_month = models.DecimalField(max_digits=2, decimal_places=0, verbose_name='Месяц текущей ЗП')
    workdays = models.DecimalField(max_digits=2, decimal_places=0, verbose_name='Кол-во рабочих дней')
    payment = models.BooleanField(default=False, verbose_name='Статус выплаты ЗП')
    salary_total = models.DecimalField(max_digits=6, decimal_places=1, verbose_name='Итого ЗП за тек.месяц')
    salary_nal_term_corp = models.DecimalField(max_digits=6, decimal_places=1, verbose_name='ЗП нал+терминал+корп')
    salary_airport = models.DecimalField(max_digits=6, decimal_places=1, verbose_name='ЗП со стойки')
    fuel = models.IntegerField(default=0, verbose_name='Коэффициент за эконом топлива')
    fuel_bonus = models.DecimalField(max_digits=6, decimal_places=1, default=0, verbose_name='Премия за эконом топлива')
    salary_add = models.DecimalField(max_digits=6, decimal_places=1, verbose_name='ЗП доначислено')
    salary_add_comment = models.TextField(max_length=200, verbose_name='Комментарий к ЗП доначислено')
    deduction = models.DecimalField(max_digits=6, decimal_places=0, default=0, verbose_name='Удержано из ЗП')

    def get_driver_name(self):
        driver = Drivers.objects.using('Cx_TaxiConfiguration').get(id=self.driver_id)
        return driver.fullname


class Payments(models.Model):
    date = models.DateTimeField(auto_now_add=True, verbose_name='Дата документа')
    salary_id = models.DecimalField(max_digits=6, decimal_places=0, default=0, verbose_name='id ЗП = год + мес')
    driver_id = models.DecimalField(max_digits=10, decimal_places=0, verbose_name='id водителя')
    sum = models.DecimalField(max_digits=6, decimal_places=0, default=0, verbose_name='Сумма выплаты')
    sum_comment = models.TextField(max_length=200, verbose_name='Комментарий')
