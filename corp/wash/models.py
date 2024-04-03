from django.db import models


# Create your models here.


class Order(models.Model):
    dt = models.DateTimeField(verbose_name='Дата документа')
    car_number = models.CharField(null=True, max_length=20, verbose_name='Номер автомобиля')
    car_id = models.CharField(null=True, verbose_name='id авто infinity', max_length=12)
    car_type = models.CharField(max_length=10, verbose_name='Тип автомобиля')
    price_ids = models.CharField(max_length=20, verbose_name='Список id услуг')
    sum = models.DecimalField(max_digits=6, decimal_places=0, default=0, verbose_name='Стоимость услуг')
    sum_time = models.DecimalField(max_digits=3, decimal_places=0, default=0,
                                   verbose_name='Суммарное затраченное время на выполнение услуг')
    add_service = models.CharField(max_length=50, verbose_name='Наименование доп услуг')
    add_price = models.DecimalField(max_digits=6, decimal_places=0, default=0, verbose_name='Стоимость доп услуг')
    pay_type = models.CharField(max_length=30, verbose_name='Способ оплаты')
    comment = models.CharField(null=True, max_length=500, verbose_name='Комментарий')
    park_car = models.BooleanField(default=False, verbose_name='Наш автопарк')


class Price(models.Model):
    name = models.CharField(max_length=500, verbose_name='Наименование услуги')
    description = models.CharField(null=True, max_length=500, verbose_name='Описание услуги')
    price_car = models.DecimalField(max_digits=6, decimal_places=0, default=0, verbose_name='Стоимость легковой авто')
    price_crossover = models.DecimalField(max_digits=6, decimal_places=0, default=0, verbose_name='Стоимость паркетник')
    price_suv = models.DecimalField(max_digits=6, decimal_places=0, default=0, verbose_name='Стоимость внедорожник')
    comment = models.CharField(null=True, max_length=500, verbose_name='Комментарий')
    index = models.DecimalField(max_digits=3, decimal_places=0, default=0, verbose_name='Порядковый номер')
    status = models.BooleanField(default=True, verbose_name='Статус услуги')
    group = models.DecimalField(max_digits=2, decimal_places=0, default=0, verbose_name='Группа услуги')
    work_time = models.DecimalField(max_digits=3, decimal_places=0, default=0,
                                    verbose_name='Время потреченное на выполнение услуги, мин')
