# -*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from .models import Product, Category, Basket, BasketItem
import csv
import uuid
import decimal
import json
from .forms import UploadFileForm
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect

from pprint import pprint

def get_request_data(request):
    data = None
    if request.method == 'GET':
        data = request.GET
    elif request.method == 'POST':
        data = request.POST
    return data


def get_oid(request, var_name="oid"):
    """Вытащить oid из реквеста"""
    oid = None
    data = get_request_data(request)
    if data is None:
        raise ValidationError # Если я прошу oid значит он ДОЛЖЕН быть
    oid = data[var_name]
    return uuid.UUID(oid, version=4)


def get_count(scnt):
    if '.' in scnt:
        return decimal.Decimal(scnt)
    else:
        return int(scnt)



@login_required
@staff_member_required
def import_products(request):
    form = UploadFileForm(request.POST, request.FILES)
    nl = 0
    if form.is_valid(): # а куда она денется
        f = request.FILES['file']
        first = True
        reader = csv.reader(f)
        for row in reader:
            if not first:
                oid = row[0]
                article = row[1]
                shortname = row[2]
                name = row[3]
                active = row[4]
                baseprice = row[5]
                description = row[6]
                properties = row[7]

                if oid != '':
                    oid = uuid.UUID(oid, version=4)
                    try:
                        product = Product.objects.get(pk=oid)
                    except Product.DoesNotExist:
                        product = Product()
                else:
                    product = Product()
                product.article = article
                product.shortname = shortname
                product.name = name
                if active in ('1', 'True'):
                    product.active = True
                else:
                    product.active = False
                product.baseprice = decimal.Decimal(baseprice)
                if description != '':
                    product.description = description
                if properties != '':
                    try:
                        obj = json.loads(properties)
                        product.properties = properties
                    except ValueError:
                        pass # bad json
                product.save()
                nl += 1
            first = False
    return HttpResponse("Ok {} products".format(nl))


def as_s(o):
    if isinstance(o, unicode):
        return o.encode('utf-8')
    if o is None:
        return ''
    return str(o)


@login_required
@staff_member_required
def export_products(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="products.csv"'
    writer = csv.writer(response)
    writer.writerow([
        'id',
        'article',
        'shortname',
        'name',
        'active',
        'baseprice',
        'description',
        'properties',
        ])
    for obj in Product.objects.all():
        writer.writerow([
            as_s(obj.id),
            as_s(obj.article),
            as_s(obj.shortname),
            as_s(obj.name),
            as_s(obj.active),
            as_s(obj.baseprice),
            as_s(obj.description),
            as_s(obj.properties)
            ])
    return response

@login_required
@staff_member_required
def export_categorys(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="categorys.csv"'
    writer = csv.writer(response)
    writer.writerow([
        'id',
        'shortname',
        'name',
        'description',
        'active',
        'properties',
        ])
    for obj in Category.objects.all():
        writer.writerow([
            as_s(obj.id),
            as_s(obj.shortname),
            as_s(obj.name),
            as_s(obj.description),
            as_s(obj.active),
            as_s(obj.properties)
            ])
    return response

@login_required
@staff_member_required
def export_baskets(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="categorys.csv"'
    writer = csv.writer(response)
    writer.writerow([
        'user id',
        'user name',
        'user phone',
        'user email',
        'created',
        'posted',
        'modified',
        'state',
        'shortname',
        'cnt',
        'price',
        ])
    for basket in Basket.objects.filter(state=1):
        for item in basket.basketitem_set.all():
         writer.writerow([
            as_s(basket.user_id),
            as_s(basket.user_name),
            as_s(basket.user_phone),
            as_s(basket.user_email),
            as_s(basket.created),
            as_s(basket.posted),
            as_s(basket.modified),
            as_s(basket.state),
            as_s(item.shortname),
            as_s(item.cnt),
            as_s(item.price)
            ])
    return response

def get_basket(request):
    bid = request.session.get('bid', None)
    if bid is None:
        basket = Basket()
        basket.save()
        bid = basket.id
    else:
        try:
            bid = uuid.UUID(bid, version=4)
            basket = Basket.objects.get(pk=bid)
        except (ValueError, Basket.DoesNotExist):
            basket = Basket()
            basket.save()
            bid = basket.id
        except Exception as e:
            print "e=", e, type(e), Basket.DoesNotExist, type(Basket.DoesNotExist)
            raise
    if basket.state != 0:
        # Если корзина уже обработана, то пользователю с ней работать НЕЛЬЗЯ
        basket = Basket()
        basket.save()
        bid = basket.id

    request.session['bid'] = str(bid)
    return basket


def add_to_basket(request):
    """TODO CSRF переделать под POST"""
    basket = get_basket(request)
    oid = get_oid(request)
    data = get_request_data(request)
    cnt = get_count(data['count'])
    price_item = Product.objects.get(pk=oid)
    bitem = basket.basketitem_set.create(
                                         article=price_item.article,
                                         cnt=cnt,
                                         shortname=price_item.shortname,
                                         price=price_item.baseprice
                                         )
    return HttpResponse("Ok1")


def update_basket(request):
    """Изменить содержимое корзины"""
    oid = get_oid(request)
    data = get_request_data(request)
    cnt = get_count(data['cnt'])
    basket = get_basket(request)
    item = basket.basketitem_set.get(pk=oid)
    if cnt == 0 or cnt < 0:
        item.delete()
        return HttpResponse("deleted")
    else:
        item.cnt = cnt
        item.save()
        return HttpResponse("changed")


def basket_detail(request):
    """Вернет содержимое корзины в виде JSON"""
    basket = get_basket(request)
    items = []
    for item in basket.basketitem_set.all():
        items.append(
                {
                    'id': str(item.id),
                    'article': item.article,
                    'shortname': item.shortname,
                    'cnt': item.cnt,
                    'price': item.price
                }
            )
    return JsonResponse({
                         'num': basket.num,
                         'items': items
                         })


def categoryes(request):
    category_list = Category.objects.all()
    # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    # тормоза будут. Потому, что мы тянем ВСЕ категории
    # Да еще мы тянем ВСЕ включая ПОДКАТЕГОРИИ
    # И еще active=True
    if len(category_list) > 0:
        cat_id = category_list[0].id
    else:
        cat_id = None

    if 'cat_id' in request.GET:
        cat_id = uuid.UUID(request.GET['cat_id'], version=4)
    product_list = Product.objects.filter(categories=cat_id, active=True)
    paginator = Paginator(product_list, 5)
    page = request.GET.get('page')
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    return render(request,
                  'catalog.html',
                  {
                      'category_list': category_list,
                      'cat_id': cat_id,
                      'products': products,
                      'paginator': paginator
                    }
                 )


# Тут для Javascript
def get_cat_id(request):
    """Вспомогательная функция"""
    if 'cat_id' in request.GET:
        return uuid.UUID(request.GET['cat_id'], version=4)
    return None


def get_order(request, varname, dataset):
    """Вернет порядок"""
    ordr = request.GET.get(varname, None)  # если надо упорядочить
    if ordr is None:
        return dataset
    # порядок должен быть имя_поля,имя_поля,имя_поля:desc
    # если desc не найдено, то asc
    l = ordr.split(':')
    fields = l[0].split(',')
    dataset = apply(dataset, fields)
    if len(l) > 1 and l[1] == 'desc':
        dataset = dataset.desc()
    return dataset


def js_categories(request):
    """Вернет в виде json список категорий"""
    cat_id = get_cat_id(request)
    categories = Category.objects.filter(parent=cat_id, active=True)
    categories = get_order(request, 'catorder', categories)
    result = []
    for cat in categories:
        print "parent>>", type(cat.parent), cat.parent
        parent = None
        if cat.parent is not None:
            parent = cat.parent.id
        result.append({
            'id': cat.id,
            'parent': parent,
            'shortname': cat.shortname,
            'name': cat.name,
            'description': cat.description
            })
    return JsonResponse({
        'items': result
        })


def js_products(request):
    """Вернет в виде JSON список товаров"""
    cat_id = get_cat_id(request)
    product_list = Product.objects.filter(categories=cat_id, active=True)
    product_list = get_order(request, 'prodorder', product_list)
    # Если нужен пажинатор, то надо указать это
    prodinpage = request.GET.get('prodinpage', None)
    opaginator = None
    if prodinpage is not None:
        prodpage = request.GET.get('prodpage', '1')
        paginator = Paginator(product_list, int(prodinpage))
        product_list = paginator.page(int(prodpage))
        opaginator = {
            'page': int(prodpage),
            'pages': paginator.num_pages,
            'length': int(prodinpage)
            }
    result = []
    for product in product_list:
        result.append({
            'id': product.id,
            'article': product.article,
            'shortname': product.shortname,
            'name': product.name,
            'baseprice': product.baseprice,
            'description': product.description
            })

    return JsonResponse({
        'paginator': opaginator,
        'items': result
        })

def js_process_basket(request):
    """Сохранение корзины"""
    basket = get_basket(request)
    print request.POST.keys()
    basket.user_name = request.POST['name']
    basket.user_email = request.POST.get('email', '')
    basket.user_phone = request.POST.get('phone', '')
    basket.state = 1
    basket.save()

    return JsonResponse({
        'result': 'Ok'
        })

