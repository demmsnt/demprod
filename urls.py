# -*- coding: utf-8 -*-
from django.conf.urls import url

from . import views

app_name = "demprod"

urlpatterns = [
    url(r'^catalog/$', views.categoryes, name='categories'),
    url(r'^add2basket/$', views.add_to_basket, name='add_to_basket'),
    url(r'^update_basket/$', views.update_basket, name='update_basket'),
    url(r'^basket_detail/$', views.basket_detail, name='basket_detail'),
    url(r'^export_products/$', views.export_products, name='export_products'),
    url(r'^import_products/$', views.import_products, name='import_products'),
    url(r'^export_categorys/$', views.export_categorys, name='export_categorys'),
    url(r'^export_baskets/$', views.export_baskets, name='export_baskets'),
    # для AJAX
    url(r'^js/categories/$', views.js_categories, name='js_categories'),
    url(r'^js/products/$', views.js_products, name='js_products'),
    url(r'^js/process_basket/$', views.js_process_basket, name='js_process_basket'),
]
