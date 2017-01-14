# -*- coding: utf-8 -*-

import uuid
from django.db import models
from django.core.exceptions import ValidationError
import json


class PropValid(models.Model):
    """Validate Properties"""
    properties = models.TextField(blank=True)

    def clean(self):
        # validate JSON description
        if self.properties is not None\
           and self.properties != '':
            try:
                obj = json.loads(self.properties)
            except ValueError:
                raise ValidationError('property field myst be valid JSON or null or empty string.')
    class Meta:
         abstract = True

    @property
    def oproperties(self):
        if self.properties is not None\
           and self.properties != '':
           return json.loads(self.properties)
        return None

    @oproperties.setter
    def oproperties(self, properties):
        if properties is None or properties == '':
            self.properties = None
        else:
            self.properties = json.dumps(properties)


class Product(PropValid):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    article = models.CharField(blank=False, unique=True, max_length=50)
    shortname = models.CharField(blank=False, max_length=100)
    name = models.CharField(blank=True, max_length=500)
    active = models.BooleanField(default=True)
    baseprice = models.DecimalField(blank=False, max_digits=18, decimal_places=2)
    description = models.TextField(blank=True)
    categories = models.ManyToManyField('Category', blank=True)

    def __str__(self):
        return "{}: {} ({})".format(self.article.encode('utf-8'),
                                    self.shortname.encode('utf-8'),
                                    self.baseprice)

    class Meta:
        ordering = ('shortname',)


class Picture(models.Model):
    """path - url 4 picture (maybe trailing path)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    description = models.CharField(blank=True, max_length=500)
    ordr = models.IntegerField(default=0)
    path = models.CharField(blank=False, max_length=500)
    products = models.ForeignKey(Product, on_delete=models.CASCADE)

    class Meta:
        ordering = ('ordr', 'path',)


class Category(PropValid):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    parent = models.ForeignKey('self', blank=True, null=True)
    shortname = models.CharField(blank=False, unique=True, max_length=100)
    name = models.CharField(blank=True, max_length=500)
    description = models.TextField(blank=True)
    active = models.BooleanField(default=True)
#    products = models.ManyToManyField(Product, blank=True)

    def __str__(self):
        name = self.name
        if name is None:
            name = ""
        return "{} ({})".format(self.shortname.encode('utf-8'),
                                name.encode('utf-8')
                                )

    class Meta:
        ordering = ('shortname',)
        verbose_name_plural = 'Categories'


STATE_CHOICES = ((0, 'New'),
                 (1, 'Saved'),
                 (2, 'Processed'),
                 (-1, 'Broken')
                 )

def increment_basket_num():
    """Предполагается, что корзины не будут удаляться"""
    last_basket = Basket.objects.all().order_by('num').last()
    if not last_basket:
        return 0
    return last_basket.num


class Basket(PropValid):
    """
    state - The basket State
            0: New (user work with Basket)
            1: Saved (user is finished, waiting for treatment)
            2: Processed
           -1: Broken
    """
    #num = models.AutoField(editable=False)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    num = models.IntegerField(default=increment_basket_num, editable=False)
    user_id = models.UUIDField(default=uuid.uuid4)
    # Пока пользователь не заполнит мы не знаем этих данных
    user_name = models.CharField(blank=True, max_length=200)
    user_phone = models.CharField(blank=True, max_length=20)
    user_email = models.EmailField(blank=True)
    created = models.DateTimeField(editable=False, auto_now_add=True)
    posted = models.DateTimeField(editable=False, auto_now_add=True)
    modified = models.DateTimeField(editable=False, auto_now=True)
    state = models.IntegerField(default=0, choices=STATE_CHOICES)

    class Meta:
        ordering = ('posted', 'created',)


class BasketItem(PropValid):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    article = models.CharField(blank=False, max_length=50)
    shortname = models.CharField(blank=False, max_length=100)
    cnt = models.DecimalField(blank=False, max_digits=18, decimal_places=2)
    price = models.DecimalField(blank=False, max_digits=18, decimal_places=2)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    basket_ref = models.ForeignKey(Basket, on_delete=models.CASCADE)

    @property
    def sum(self):
        return self.cnt * self.price

    class Meta:
        ordering = ('article', 'cnt',)
