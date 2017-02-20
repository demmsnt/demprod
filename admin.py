# -*- coding: utf-8 -*-
"""admin"""

from django.contrib import admin
from .models import Picture, Product, Category, BasketItem, Basket, PageFields
from cms.admin.pageadmin import PageAdmin
from cms.models.pagemodel import Page


# Не работает :-(
# class PageFieldsAdmin(admin.TabularInline):
#     model = PageFields

# PageAdmin.inlines.append(PageFieldsAdmin)

# admin.site.unregister(Page)
# admin.site.register(Page, PageAdmin)


class PictureInline(admin.TabularInline):
    model = Picture
    extra = 2
    fields = [
        'description',
        'ordr',
        'path'
        ]


class ProductAdmin(admin.ModelAdmin):
    fields = [
        'article',
        'shortname',
        'name',
        'active',
        'baseprice',
        'properties',
        'description',
        'categories'
        ]

    list_display = (
        'article',
        'shortname',
        'name',
        'active',
        'baseprice'
        )

    search_fields = ['article', 'shortname']

    inlines = [PictureInline]


admin.site.register(Product, ProductAdmin)


class CategoryAdmin(admin.ModelAdmin):
    fields = [
        'parent',
        'shortname',
        'name',
        'description',
        'active',
        'properties'
        ]

    list_display = (
        'shortname',
        'name',
        'description',
        'active'
        )

    search_fields = ['shortname']


admin.site.register(Category, CategoryAdmin)


class BasketItemInline(admin.TabularInline):
    model = BasketItem
    fields = [
        'article',
        'shortname',
        'cnt',
        'price',
        'properties',
        'created',
        'modified'
    ]


class BasketAdmin(admin.ModelAdmin):
    #exclude = ('num', 'created', 'posted', 'modified')
    #readonly_fields = ('num', 'created', 'posted', 'modified')
    fields = [
    #    'num',
        'user_id',
        'user_name',
        'user_phone',
        'user_email',
        #'created',
        #'posted',
        #'modified',
        'state',
        'properties'
        ]
    list_display = (
        'user_id',
        'user_name',
        'user_phone',
        'user_email',
        'created',
        'posted',
        'modified',
        'state',
        )

admin.site.register(Basket, BasketAdmin)
