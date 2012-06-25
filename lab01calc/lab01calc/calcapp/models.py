# -*- coding: utf-8 -*-
from django.db import models

#
class Order(models.Model):
    date = models.CharField(max_length=30, help_text='дата заказа')
    email = models.EmailField(help_text='почта заказчика')
    telephone = models.CharField(max_length=30, help_text = "телефон заказчика", blank=True)
    on_paper = models.IntegerField(help_text='изделий на листе')
    chroma = models.IntegerField(help_text='цветность 1+0 ето 10, 11 - 1+1 и т.д.')
    finally_production = models.IntegerField(help_text='итого изделий')
    list_format = models.CharField(max_length=3, help_text='формат печатного листа')
    h_list = models.IntegerField(help_text='высота печатного листа')
    w_list = models.IntegerField(help_text='ширина печатного листа')
    paper = models.CharField(max_length=20, help_text='плотность бумаги')
    height = models.FloatField(help_text='высота изделия')
    width = models.FloatField(help_text='ширина изделия')
    number_of_lists = models.IntegerField(help_text='количество печатных листов')
    quant = models.IntegerField(help_text='тираж')
    time = models.IntegerField(help_text='время на изготовление')
    type = models.CharField(max_length=20, help_text='тип печати')
    slices = models.IntegerField(help_text='количество резов')
    print_cost = models.FloatField(help_text='стоимость печати')
    slice_cost = models.FloatField(help_text='стоимость подрезки')
    big_count = models.IntegerField(null=True, blank=True, help_text='количество бигов')
    big_align = models.CharField(max_length=15, blank=True, help_text='тип биговки')
    big_cost = models.FloatField(null=True, blank=True, help_text='стоимость биговки')
    lamin_name = models.CharField(max_length=25, blank=True, help_text='тип ламинации')
    product_cost = models.FloatField(help_text="цена за 1 изделие", null=True)
    lamin_cost = models.FloatField(null=True, blank=True, help_text='стоимость ламинации')
    order_cost = models.FloatField(help_text='общая стоимость')
    layout = models.CharField(max_length=20000, blank=True)

    class Meta:
        verbose_name = u'Заказ'
        verbose_name_plural = u'Заказы'

    def __unicode__(self):
        return self.date

class Stats(models.Model):
    date = models.CharField(max_length=30, help_text='дата заказа')
    #on_paper = models.IntegerField(help_text='изделий на листе')
    chroma = models.IntegerField(null=True, blank=True, help_text='цветность 1+0 ето 10, 11 - 1+1 и т.д.')
    finally_production = models.IntegerField(null=True, blank=True, help_text='итого изделий')
    list_format = models.CharField(blank=True, max_length=3, help_text='формат печатного листа')
    h_list = models.IntegerField(null=True, blank=True, help_text='высота печатного листа')
    w_list = models.IntegerField(null=True, blank=True, help_text='ширина печатного листа')
    paper = models.CharField(blank=True, max_length=20, help_text='плотность бумаги')
    height = models.FloatField(null=True, blank=True, help_text='высота изделия')
    width = models.FloatField(null=True, blank=True, help_text='ширина изделия')
    number_of_lists = models.IntegerField(null=True, blank=True, help_text='количество печатных листов')
    quant = models.IntegerField(null=True, blank=True, help_text='тираж')
    on_paper = models.FloatField(help_text = 'количество изделий на листе')
    time = models.IntegerField(null=True, blank=True, help_text='время на изготовление')
    type = models.CharField(blank=True, max_length=20, help_text='тип печати')
    slices = models.IntegerField(null=True, blank=True, help_text='количество резов')
    print_cost = models.FloatField(null=True, blank=True, help_text='стоимость печати')
    slice_cost = models.FloatField(null=True, blank=True, help_text='стоимость подрезки')
    big_count = models.IntegerField(null=True, blank=True, help_text='количество бигов')
    big_align = models.CharField(max_length=15, blank=True, help_text='тип биговки')
    big_cost = models.FloatField(null=True, blank=True, help_text='стоимость биговки')
    lamin_name = models.CharField(max_length=25, blank=True, help_text='тип ламинации')
    product_cost = models.FloatField(help_text="цена за 1 изделие", null=True)
    lamin_cost = models.FloatField(null=True, blank=True, help_text='стоимость ламинации')
    order_cost = models.FloatField(help_text='общая стоимость')
    layout = models.CharField(max_length=20000, blank=True)

    class Meta:
        verbose_name = u'Статистика'
        verbose_name_plural = u'Статистика'

    def __unicode__(self):
        return self.date

class Paper_params(models.Model):
    param_name = models.CharField(max_length=10, help_text='плотность бумаги кирилическое')
    param_value = models.CharField(max_length=10, help_text='плотность бумаги кодовое')

    class Meta:
        verbose_name = u'Плотность бумаг'
        verbose_name_plural = u'Плотность бумаг'

    def __unicode__(self):
        return self.param_name

class Paper_price(models.Model):
    format = models.CharField(max_length=5, help_text='формат')
    chroma = models.CharField(max_length=5, help_text='цветность')
    params = models.ForeignKey(Paper_params, default=1, help_text='плотность')
    paper_cost = models.FloatField(help_text='цена')

    class Meta:
        verbose_name = u'Прайс'
        verbose_name_plural = u'Прайсы'

    def __unicode__(self):
        return self.format
'''
class Price_paper(models.Model):
    name = models.CharField(max_length=30)
    density = models.SmallIntegerField()
    cost = models.FloatField()
    def __unicode__(self):
        return self.name'''

class Size_paper(models.Model):
    name = models.CharField(max_length=20, help_text='имя формата')
    format = models.CharField(max_length=10, help_text='кодовое имя например если А4+ то кодовое А4p')
    width = models.SmallIntegerField(help_text='ширина')
    height = models.SmallIntegerField(help_text='висота')
    on_site = models.BooleanField(help_text = 'отображать на сайте')

    class Meta:
        verbose_name = u'Формат бумаги'
        verbose_name_plural = u'Форматы бумаги'

    def __unicode__(self):
        return self.name

class Constants(models.Model):
    trim = models.FloatField(help_text='допуски на подрезку') #podrezka
    print_area = models.IntegerField(help_text='допуски на запечатку') # zape4atka
    k_print_cost10 = models.FloatField(help_text='коефициент наценки на печать 1+0') # koef dryky 1+0
    k_print_cost11 = models.FloatField(help_text='коефициент наценки на печати 1+1')
    k_print_cost40 = models.FloatField(help_text='коефициент наценки на печать 4+0')
    k_print_cost44 = models.FloatField(help_text='коефициент наценки на печать 4+4')
    k_work = models.FloatField(help_text='коефициент наценки на работы') # koef robotu
    k_mater = models.FloatField(help_text='коефициент наценки на материалах') # koef materiala
    #list_size = models.ForeignKey(Size_paper, default=4) # tup lista (a3 a5 ...) 4 - a3
    email = models.CharField(max_length=30, help_text='почта исполнителя заказов')
    k_min_edition = models.FloatField(help_text='коефициент наценки на минимальный тираж') # koef minimal naklad
    min_edition = models.IntegerField(help_text='минимальный тираж') # min naklad
    k_print_slice = models.FloatField(help_text='цена 1 реза') # cina 1 riza
    k_list_slice = models.IntegerField(help_text='количество листов в 1 стопке для порезки') # k-st list u stopci
    A4 = models.FloatField(help_text='балли для просчета А4') # ballu dl9 formata A4
    A4p = models.FloatField(help_text='балли для просчета А+') # A4+
    A3 = models.FloatField(help_text='балли для просчета А3')
    A3p = models.FloatField(help_text='балли для просчета А3+')
    k_format = models.FloatField(help_text='коефициент наценки на форматы А4+ и А3+') # koef formativ+
    k_1big = models.FloatField(help_text='цена 1 бига') # cina 1 biga
    k_2big = models.FloatField(help_text='цена 2 бигов') # 2 bigiv
    k_1prildka = models.FloatField(help_text = "цена односторонней приладки для оффсета")
    k_2prildka = models.FloatField(help_text = "цена двусторонней приладки для оффсета")
    k_1printoffset = models.FloatField(help_text = "цена односторонней оффсетной печати")
    k_2printoffset = models.FloatField(help_text = "цена двусторонней оффсетной печати")
    k_form = models.FloatField(help_text = 'цена оффсетной формы')
    k_offset = models.FloatField(help_text = 'коефициент накрутки на оффсете')
    trim_offset = models.FloatField(help_text = 'допуск на подрезку в оффсете')
    print_area_offset = models.FloatField(help_text = 'допуск на запечатку в оффсете')

    class Meta:
        verbose_name = u'Константы'
        verbose_name_plural = u'Константы'

class Lamin(models.Model):
    lamin_label = models.CharField(max_length=25, help_text='Название ламинации кирилическое')
    lamin_name = models.CharField(max_length=25, help_text='Кодовое название')
    price_a4 = models.FloatField(help_text='цена за А4')
    price_a3 = models.FloatField(help_text='цена за А3')

    class Meta:
        verbose_name = u'Прайс на ламинацию'
        verbose_name_plural = u'Прайсы на ламинацию'

    def __unicode__(self):
        return self.lamin_label

class OffsetPrice(models.Model):
    density = models.IntegerField(help_text = 'плотность бумаги')
    price = models.FloatField(help_text='цена за А2')

    class Meta:
        verbose_name = u'Прайс на оффсет'
        verbose_name_plural = u'Прайсы на оффсет'


'''class Price_printing(models.Model):
    thickness = models.FloatField()
    print_price = models.FloatField()
    def __unicode__(self):
        return self.print_price'''