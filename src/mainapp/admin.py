# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import *


class AllFieldsModelAdmin(admin.ModelAdmin):

    def __init__(self, model, admin_site):
        self.list_display = [field.name for field in model._meta.fields if field.name != "id"]
        super(AllFieldsModelAdmin, self).__init__(model, admin_site)


class TickerAdmin(AllFieldsModelAdmin):
    search_fields = ('symbol', 'security_name', )
    list_filter = ('market_category', )

admin.site.register(Ticker, TickerAdmin)


class PriceAdmin(AllFieldsModelAdmin):
    pass

admin.site.register(Price, PriceAdmin)


class InsiderTradeAdmin(AllFieldsModelAdmin):
    search_fields = ('insider', )
    list_filter = ('transaction_type', )

admin.site.register(InsiderTrade, InsiderTradeAdmin)
