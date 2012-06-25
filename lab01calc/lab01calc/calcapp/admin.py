# -*- coding: utf-8 -*-
from django.contrib import admin
from calcapp.models import Constants, Size_paper, Order, Paper_params, Paper_price, Lamin, OffsetPrice, Stats
from django.conf import settings

class Size_paperAdmin(admin.ModelAdmin):
    list_display = ('name', 'format', 'width', 'height')

class Paper_priceAdmin(admin.ModelAdmin):
    list_display = ('format', 'chroma', 'params', 'paper_cost')

class OrderAdmin(admin.ModelAdmin):

    class Media:
        #paths =   "%sjs/some_js.js".format({{ MEDIA_URL }}) #%()
        #paths = str({{MEDIA_URL}})

        jsfile = 'js/some_js.js'
        pathjs = settings.MEDIA_URL + jsfile
        js = ( pathjs, )
    list_display = ('id', 'date', 'email', 'type', 'time')
class StatsAdmin(admin.ModelAdmin):
    class Media:
        #paths =   "%sjs/some_js.js".format({{ MEDIA_URL }}) #%()
        #paths = str({{MEDIA_URL}})

        jsfile = 'js/some_js.js'
        pathjs = settings.MEDIA_URL + jsfile
        js = ( pathjs, )
    list_display = ('id', 'date', 'type', 'time')

class LaminAdmin(admin.ModelAdmin):
    list_display = ('lamin_label', 'price_a4', 'price_a3')

class OffsetPriceAdmin(admin.ModelAdmin):
    list_display = ('density', 'price')

admin.site.register(Constants)
admin.site.register(Size_paper, Size_paperAdmin)
admin.site.register(Lamin)
admin.site.register(Paper_params)
admin.site.register(Paper_price, Paper_priceAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OffsetPrice, OffsetPriceAdmin)
admin.site.register(Stats, StatsAdmin)


