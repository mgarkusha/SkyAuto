from django.db import models
from infinity.models import Drivers, Cars


# Create your models here.
class Smena(models.Model):
    number = models.DecimalField(max_digits=6, decimal_places=0, verbose_name='Номер документа')
    date = models.DateTimeField(auto_now_add=True, verbose_name='Дата документа')
    driver_id = models.DecimalField(max_digits=10, decimal_places=0, verbose_name='id водителя')
    start_date = models.DateTimeField(verbose_name='Начало периода')
    finish_date = models.DateTimeField(verbose_name='Конец периода')
    proceeds_cash = models.DecimalField(max_digits=6, decimal_places=0, verbose_name='Наличные')
    proceeds_cash_orders = models.DecimalField(max_digits=6, decimal_places=0, verbose_name='Кол-во заказов Наличные')
    proceeds_terminal = models.DecimalField(max_digits=6, decimal_places=0, verbose_name='Банковский терминал')
    proceeds_terminal_orders = models.DecimalField(max_digits=6, decimal_places=0,
                                                   verbose_name='Кол-во заказов Банковский терминал')
    proceeds_corporate_bank = models.DecimalField(max_digits=6, decimal_places=0, verbose_name='Безналичный равсчёт')
    proceeds_corporate_bank_orders = models.DecimalField(max_digits=6, decimal_places=0,
                                                         verbose_name='Кол-во заказов Безналичный равсчёт')
    spending_fuel_cash = models.DecimalField(max_digits=6, decimal_places=0, verbose_name='Бензин')
    spending_fuel_litres = models.DecimalField(max_digits=6, decimal_places=0, verbose_name='Бензин, литры')
    spending_carwash = models.DecimalField(max_digits=6, decimal_places=0, verbose_name='Мойка авто')
    spending_carwash_bank = models.DecimalField(max_digits=6, decimal_places=0, verbose_name='Мойка авто безнал')
    spending_parking = models.DecimalField(max_digits=6, decimal_places=0, verbose_name='Парковка')
    spending_washer = models.DecimalField(max_digits=6, decimal_places=0, verbose_name='Омывайка')
    spending_to = models.DecimalField(max_digits=6, decimal_places=0, verbose_name='Тех.осмотр')
    spending_lamp = models.DecimalField(max_digits=6, decimal_places=0, verbose_name='Лампочки')
    spending_repair = models.DecimalField(max_digits=6, decimal_places=0, verbose_name='Ремонт')
    spending_etc = models.DecimalField(max_digits=6, decimal_places=0, verbose_name='Прочие расходы')
    spending_etc_comment = models.TextField(max_length=200, verbose_name='Комментарий к доп. расходам')
    spending = models.DecimalField(max_digits=6, decimal_places=0, verbose_name='Итого расходы')
    money_to_boss = models.DecimalField(max_digits=6, decimal_places=0, verbose_name='К сдаче')
    money_to_boss_fact = models.DecimalField(max_digits=6, decimal_places=0, verbose_name='Фактически сдал')
    debt = models.DecimalField(max_digits=6, decimal_places=0, verbose_name='Долг')
    debt_comment = models.TextField(max_length=200, verbose_name='Комментарий к долгу')
    fuel_consumption = models.DecimalField(max_digits=3, decimal_places=1, default=0,
                                           verbose_name='Средний расход топлива, л')

    def get_driver_name(self):
        driver = Drivers.objects.using('Cx_TaxiConfiguration').get(id=self.driver_id)
        return driver.fullname


class Run(models.Model):
    smena_id = models.ForeignKey(Smena, on_delete=models.CASCADE, verbose_name='id Смены')
    car_id = models.DecimalField(max_digits=10, decimal_places=0, verbose_name='id Авто')
    run = models.DecimalField(max_digits=6, decimal_places=0, verbose_name='Пробег за смену, км')
    start_km = models.DecimalField(max_digits=7, decimal_places=0, default=0,
                                   verbose_name='Пробег на открытие смены, м')
    finish_km = models.DecimalField(max_digits=7, decimal_places=0, default=0,
                                    verbose_name='Пробег на закрытие смены, км')
