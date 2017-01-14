'use strict';
// ================== [Защита] ==================================
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        function getCookie(name) {
            var cookieValue = null;
            if (document.cookie && document.cookie != '') {
                var cookies = document.cookie.split(';');
                for (var i = 0; i < cookies.length; i++) {
                    var cookie = jQuery.trim(cookies[i]);
                    // Does this cookie string begin with the name we want?
                    if (cookie.substring(0, name.length + 1) == (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }
        if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
            // Only send the token to relative URLs i.e. locally.
            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
        }
    }
});
// ==============================================================
function checkout() {
    //Надо проверить что корзина не пустая

    function make_modal() {
        $('<div id="dlg_modal" class="modal fade" role="dialog"></div>').appendTo('body');
        $('<div class="modal-dialog"></div>').appendTo('#dlg_modal');
        $('<div class="modal-content"></div>').appendTo('#dlg_modal .modal-dialog');
        $('<div class="modal-header"></div>').appendTo('#dlg_modal .modal-content');
        $('<button type="button" class="close" data-dismiss="modal">&times;</button>').appendTo('#dlg_modal .modal-header');
        $('<h4 class="modal-title">оформить заказ</h4>').appendTo('#dlg_modal .modal-header');
        $('<div class="modal-body"></div>').appendTo('#dlg_modal .modal-content');

        $('<div class="form-group user-name"></div>').appendTo('#dlg_modal .modal-body');
        $('<label class="control-label">Ваше имя</label>').appendTo('#dlg_modal .user-name');
        $('<input class="form-control" name="user-name">').appendTo('#dlg_modal .user-name');

        $('<div class="form-group user-phone"></div>').appendTo('#dlg_modal .modal-body');
        $('<label class="control-label">Ваш телефон</label>').appendTo('#dlg_modal .user-phone');
        $('<input class="form-control" name="user-phone">').appendTo('#dlg_modal .user-phone');

        $('<div class="form-group user-email"></div>').appendTo('#dlg_modal .modal-body');
        $('<label class="control-label">Ваш e-mail</label>').appendTo('#dlg_modal .user-email');
        $('<input class="form-control" type="email" name="user-email">').appendTo('#dlg_modal .user-email');

        $('<div class="modal-footer"></div>').appendTo('#dlg_modal .modal-content');
        $('<button type="button" class="btn btn-default" data-dismiss="modal">Close</button>').appendTo('#dlg_modal .modal-footer');
        $('<button type="button" class="btn btn-default modal-select-btn">Ok</button>').appendTo('#dlg_modal .modal-footer');
        return $('#dlg_modal');
    }
    var modal = make_modal();
    modal.modal('show');

    //удалим
    $('#dlg_modal').on('hidden.bs.modal', function() {
        $('#dlg_modal').remove();
    });

    $('#dlg_modal .modal-select-btn').bind('click', function() {
        var data = {
            username: $('#dlg_modal [name="user-name"]').val(),
            phone: $('#dlg_modal [name="user-phone"]').val(),
            email: $('#dlg_modal [name="user-email"]').val()
        };
        //тут сделать проверку
        console.log("data=", data);
        modal.modal('hide');
    });

}


function show_basket(urls) {
    var url = urls.basket_detail;

    // -----------------------------------------
    function draw_basket(data) {
        //спрячем кнопку
        $('#show_basket').css({ 'display': 'none' });
        $('<div id="basket"><div id="close_basket"><a href="#">[X]</a></div></div>').appendTo('body');
        if (data.items.length == 0) {
            $('Корзина пустая').appendTo('#basket');
        } else {
            $('<div>Номер заказа ' + data.num + '</div>').appendTo('#basket')
            $('<div class="basket_list"></div>').appendTo('#basket');

            $.each(data.items, function(idx, o) {
                var html = '<input type="text" maxlength="3" class="form-control" value="' + o.cnt + '"><button class="btn btn-default change_cnt">Изменить</button><button class="btn btn-default del_item">Удалить</button>';
                $('<div class="basket_item form-group" data-id="' + o.id + '">' + o.article + ')' + o.shortname + '(' + o.price + ')' + html + '</div>').appendTo('#basket .basket_list');
            });
            $('<a href="#" id="checkout">Оформить заказ</a>').appendTo('#basket');
        }

        $('#checkout').bind('click', checkout);
        $('.basket_list .del_item').bind('click', function(evt) {
            var row = $(evt.currentTarget).parents('div.basket_item')[0];
            var id = $(row).data('id');
            $.post(urls.update_basket,
                { oid: id, cnt: "0" }
            ).done(
                function(data) {
                    if (data == 'deleted') {
                        $(row).remove();
                    }
                }
            );
        });
        $('.basket_list .change_cnt').bind('click', function(evt) {
            var row = $(evt.currentTarget).parents('div.basket_item')[0];
            var id = $(row).data('id');
            var cnt = $(row).find('input').val()
            $.post(urls.update_basket,
                   { oid: id, cnt: cnt }
            ).done(
                function(data) {
                    if (data == 'deleted') {
                        $(row).remove();
                    }
                }
            );
        });

        $('#close_basket').bind('click', function() {
            $('#basket').remove();
            $('#show_basket').css({ 'display': 'block' });
        });
    }
    // -----------------------------------------

    $.get(url, draw_basket);
}



// --------------------------------------------------------------
function int_demprod(urls) {
    $('#show_basket').bind('click', function() { show_basket(urls) });
    $('.product').bind('click', function(evt) {
        var id = $(evt.currentTarget).data('id');
        $.get(
            urls.add_to_basket + "?oid=" + id + "&count=1",
            function(data) {
                alert('Товар добавлен в корзину'); // + data + $(evt.currentTarget).data('id'));
            }
        );
    });

}
// --------------------------------------------------------------
// $( document ).ready(function() {
//   int_demprod();
// });

// --------------------------------------------------------------
// Ajax рисование (Вообще тут надо шаблонизатор, ну а пока пойдет и так)
// --------------------------------------------------------------
// Категории
function draw_categories(urls, target, options) {
    $.get(
        urls.js_categories
    ).done(function(data) {
        $(target).html('');
        if (data.items.length == 0) {
            $(target).html('Категорий нет');
        } else {

        }
    });
}
//Товары
function draw_products(urls, target, options) {
    $.get(
        urls.js_products
    ).done(function(data) {
        $(target).html('');
        if (data.items.length == 0) {
            $(target).html('Товаров нет');
        } else {
            $('<table class="table table-striped"></table>').appendTo(target);
            $('<thead></thead>').appendTo(target+' table');
            $('<tr><th>#</th><th>Артикул</th><th>Кр.имя</th><th>Имя</th><th>Примечание</th></tr>').appendTo(target+' table thead');
            $.each(data.items, function (idx, o){
              $('<tr data-id="'+o.id+'"><td>'+idx+'</td><td>'+o.article+'</td><td>'+o.shortname+'</td><td>'+o.name+'</td><td>'+o.description+'</td></tr>').appendTo(target+' table');
            });

        }
    });
}

// --------------------------------------------------------------
// тестируем
// --------------------------------------------------------------
function test_ajax(urls, options) {
        draw_categories(urls, '#cat_target');
        draw_products(urls, '#prod_target');
}