# -*- coding: utf-8 -*-
from django.contrib import auth
from django.http import HttpResponse, HttpResponseBadRequest, Http404, HttpResponseRedirect
from django.core.mail import EmailMessage
from django.shortcuts import render_to_response, render
from django.template.context import RequestContext
from django.utils import simplejson
from calcapp.models import Constants, Size_paper, Order, Paper_price, Paper_params, Lamin
import math
import datetime
#from django_dropbox import storage
#from dropbox import client, rest, session
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
from django.middleware.csrf import get_token
from django.core.context_processors import csrf
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_protect, requires_csrf_token, ensure_csrf_cookie, csrf_exempt

# ------------------------------------get all paper density
def paper_choose(request):
   try:
            params = {'Paper' : list(Paper_params.objects.values('param_name', 'param_value'))}
            json = simplejson.dumps(params, ensure_ascii=False, indent=4)
            return HttpResponse(json, mimetype='application/json; charset=utf-8')
   except:
        params = {"Oops something wrong." : "Error"}
        json = simplejson.dumps(params)
        return HttpResponse(json, mimetype='application/json', status=406)


# -------------------------------------main counter
def recounter(request):
        pos = False
        i = 0
        adds = {}

#    try:
        # check request
        if 'height' and 'width' and 'add_trim' and 'add_print_area' and 'quant' in request.GET and request.GET['add_trim'] and request.GET['add_print_area'] and request.GET['quant']:
            # get vars from request
            add_trim = request.GET['add_trim'] # check trim
            add_print_area = request.GET['add_print_area'] # check print_area
            quant = int(request.GET['quant'])
            width = int(request.GET['width'])
            height = int(request.GET['height'])
            # from db get paper formats
            qr = Size_paper.objects.all()[:4].values('format','width', 'height')
            # from db get points for formats and value of trim and add_print
            qrk = Constants.objects.filter(pk=1).values('A4','A4p','A3','A3p', 'trim', 'print_area')
            # push to arrays
            point_wlist = [qr[0]["width"], qr[1]["width"], qr[2]["width"], qr[3]["width"]] # width of formats
            point_hlist = [qr[0]["height"], qr[1]["height"], qr[2]["height"], qr[3]["height"]] # height of formats
            k_format_list = [qrk[0]["A4"], qrk[0]["A4p"], qrk[0]["A3"], qrk[0]["A3p"]] # points of formats
            formats = [qr[0]["format"], qr[1]["format"], qr[2]["format"], qr[3]["format"]] # name of formats
            # check add or remove trim and print_area
            if add_trim == 'true': dop = 0
            else: dop = qrk[0]["trim"]
            if add_print_area == 'true': pod = 0
            else: pod = qrk[0]["print_area"]
            # get list width & height
            '''if 'list_width' in request.GET and request.GET['list_width']:
                wid_a3 = int(request.GET['list_width'])
            else:
                wid_a3 = int(Size_paper.objects.get(format = format).width)
            if 'list_height' in request.GET and request.GET['list_height']:
                hei_a3 = int(request.GET['list_height'])
            else:
                hei_a3 = int(Size_paper.objects.get(format = format).height)'''
            # points of formats
            all_points = [0, 0, 0, 0]
            # width and height of product
            wid_cut, hei_cut = width + 2 * dop, height + 2 * dop
            # loop through formats and count point for each
            for i in range(4):
                wid_paper = 0
                hei_paper = 0
                # width, height and point of formats from arrays
                wid_a3 = point_wlist[i]
                hei_a3 = point_hlist[i]
                k_format = k_format_list[i]
                # size of format with print_area
                wid_paper, hei_paper = wid_a3 - pod * 2, hei_a3 - pod * 2
                x1 = int(wid_paper / wid_cut) #  quant of cols in vertical layout
                y1 = int(hei_paper / hei_cut) # rows
                z1 = x1 * y1 # how many products
                z1 = math.floor(z1)
                x2 = int(wid_paper / hei_cut) # same for horizontal layout
                y2 = int(hei_paper / wid_cut)
                z2 = x2 * y2
                z2 = math.floor(z2)
                # if product too big for this format get another
                if z1 == 0 and z2 == 0:
                    continue
                elif z1 > z2: # if vertical layout better make count on
                    paper_quant = quant / float(z1)
                    on_paper = z1 # quant of products on 1 list
                    slices = (x1 + y1 + 4) - 2 # рахуємо різи
                    rows = y1 # рядки в розкладці
                    cols = x1 # стовці
                    pos = True # this is vertical layout
                else: # horizontal is better
                    paper_quant = quant / float(z2)
                    on_paper = z2
                    slices = (x2 + y2 + 4) - 2
                    rows = y2
                    cols = x2
                    pos = False # this is horizontal layout
                paper_quant = math.ceil(paper_quant)
                # count points for format
                weight = on_paper * k_format
                # push to array
                all_points[i] = weight
                # push all about this format
                adds[i] =  {"paper_quant": paper_quant, "slices":slices, "rows":rows, "cols":cols, "pos":pos, "on_paper":on_paper}
            # get index of best format
            maxx = all_points.index(max(all_points))
            # get adds of best format
            paper_quant = adds[maxx]["paper_quant"]
            slices = adds[maxx]["slices"]
            rows = adds[maxx]["rows"]
            cols = adds[maxx]["cols"]
            pos = adds[maxx]["pos"]
            wid_a3 = point_wlist[maxx]
            hei_a3 = point_hlist[maxx]
            formatt = formats[maxx] # name of format
            on_paper = adds[maxx]["on_paper"]
            '''if maxx == 0:
                formatt = "A4"
                wid_a3 = point_wlist[0]
                hei_a3 = point_hlist[0]
                paper_quant = adds[0]["paper_quant"]
                slices = adds[0]["slices"]
                rows = adds[0]["rows"]
                cols = adds[0]["cols"]
                pos = adds[0]["pos"]
            elif maxx == 1:
                formatt = "A4p"
                wid_a3 = point_wlist[1]
                hei_a3 = point_hlist[1]
                paper_quant = adds[1]["paper_quant"]
                slices = adds[1]["slices"]
                rows = adds[1]["rows"]
                cols = adds[1]["cols"]
                pos = adds[1]["pos"]
            elif maxx == 2:
                formatt = "A3"
                wid_a3 = point_wlist[2]
                hei_a3 = point_hlist[2]
                paper_quant = adds[2]["paper_quant"]
                slices = adds[2]["slices"]
                rows = adds[2]["rows"]
                cols = adds[2]["cols"]
                pos = adds[2]["pos"]
            elif maxx == 3:
                formatt ="A3p"
                wid_a3 = point_wlist[3]
                hei_a3 = point_hlist[3]
                paper_quant = adds[3]["paper_quant"]
                slices = adds[3]["slices"]
                rows = adds[3]["rows"]
                cols = adds[3]["cols"]
                pos = adds[3]["pos"]
            wid_cut = 0
            hei_cut = 0
            wid_paper = 0
            hei_paper = 0
            wid_cut, hei_cut = width + 2 * dop, height + 2 * dop #  ширина висота макета з обрізуванням
            wid_paper, hei_paper = wid_a3 - pod * 2, hei_a3 - pod * 2 # запечатка
            x1 = int(wid_paper / wid_cut) #  кількість стовпців у вертикальній розкладці
            y1 = int(hei_paper / hei_cut) # кількість рядків
            z1 = x1 * y1 # їх площа
            z1 = math.floor(z1)
            x2 = int(wid_paper / hei_cut) # те саме для горизонтальної розкладки
            y2 = int(hei_paper / wid_cut)
            z2 = x2 * y2
            z2 = math.floor(z2)
            if z1 == 0 and z2 == 0:
                json = simplejson.dumps({"Something wrong" : "or error were occured"})
                return HttpResponse(json, mimetype='application/json', status=406)
            elif z1 > z2:
                paper_quant = quant / float(z1)
                on_paper = z1
                slices = (x1 + y1 + 4) - 2 # рахуємо різи
                rows = y1 # рядки в розкладці
                cols = x1 # стовці
                pos = True
            else:
                paper_quant = quant / float(z2)
                on_paper = z2
                slices = (x2 + y2 + 4) - 2
                rows = y2
                cols = x2
                pos = False
            paper_quant = math.ceil(paper_quant)'''
            # how many material need for all product
            perfect = quant * width * height
            # real quant of material are used
            got = paper_quant * wid_a3 * hei_a3
            # how many material aren't use
            per = (1 - (perfect / got)) * 100
            per = round(per, 2)
            # how many products finally get
            all_prod = paper_quant * on_paper
            # all params
            params = {"width" : width, "height" :height, "Real": perfect, "All": got, "Out" : per, "On_paper" : on_paper, "number_of_lists" : paper_quant, "finally_production" : all_prod, "wid_a3" : wid_a3, "hei_a3" : hei_a3, "slices" : slices, "cols" : cols, "rows" : rows, "pos" : pos, "trim" : pod, "dop" : dop, "points" : all_points, "max": maxx, "format": formatt, "wid_paper":wid_paper, "hei_paper": hei_paper, "wid_cut": wid_cut, "hei_cut":hei_cut, "adds":adds, "maxx":maxx}
            # dumps they to json
            json = simplejson.dumps(params, indent=4)
            return HttpResponse(json, mimetype='application/json')
        else:
            json = simplejson.dumps({"Some parameters" : "were not sent"})
            return HttpResponse(json, mimetype='application/json', status=406)
#    except:
#        params = {"Oops something wrong." : "Error"}
#        json = simplejson.dumps(params)
#        return HttpResponse(json, mimetype='application/json', status=406)



# ---------------------------------------------------------cost counter
def digit(request):

#    try:
        if 'param_value' and 'chroma' and 'number_of_lists' and 'format' in request.GET and request.GET['format']  and request.GET['param_value'] and request.GET['chroma']:
            params = request.GET['param_value']
            d = Paper_params.objects.get(param_value=params) # paper density from db
            chroma = int(request.GET['chroma'])
            quant = int(request.GET['quant'])
            format = request.GET['format']
            frm = format[:2]
            # get constants from db
            qrk = Constants.objects.filter(pk = 1).values('min_edition', 'k_min_edition','k_list_slice','k_print_slice','k_format', 'k_1big','k_2big')
            # from request get number of list
            if 'number_of_lists' in request.GET and request.GET['number_of_lists']:
                number_of_lists = int(request.GET['number_of_lists'])
            elif 'number_of_lists' in request.GET:
                number_of_lists = int(request.GET['quant'])
            # get cost from db
            if chroma == 10:
                paper_cost = Paper_price.objects.get(chroma="1+0", format = frm, params=d.id).paper_cost
            elif chroma == 11:
                paper_cost = Paper_price.objects.get(chroma="1+1", format = frm, params=d.id).paper_cost
            elif chroma == 40:
                paper_cost = Paper_price.objects.get(chroma="4+0", format = frm, params=d.id).paper_cost
            elif chroma == 44:
                paper_cost = Paper_price.objects.get(chroma="4+4", format = frm, params=d.id).paper_cost
            order_cost = paper_cost * number_of_lists
            print_cost = order_cost
            print_cost = round(print_cost, 3)
            min_edition = qrk[0]['min_edition'] # minimal number of products
            k_min_edition = qrk[0]['k_min_edition'] # koef for minimal
            # over cost for minimal number of products
            if number_of_lists <= min_edition:
                order_cost = order_cost * k_min_edition
            # cost for cutting
            if 'slices' in request.GET and request.GET['slices']:
                slices = int(request.GET['slices'])
                k_cost_slice = qrk[0]['k_print_slice'] # дістаємо ціну за різ
                k_list_slice = qrk[0]['k_list_slice'] # дістаємо кількість листів у стопці
                stopok = float(number_of_lists) / k_list_slice
                stopok = math.ceil(stopok)
                slice_cost = stopok * slices * k_cost_slice # вартість порізки
                order_cost = order_cost + slice_cost
            # cost for bigovka)
            if 'add_big' in request.GET:
                big = request.GET['add_big']
                if big == 'true':
                    big_count = int(request.GET['big_count'])
                    big_align = request.GET['big_align']
                    if big_count == 1:
                        k_big = qrk[0]['k_1big']
                    elif big_count == 2:
                        k_big = qrk[0]['k_2big']
                    big_cost = quant * k_big
                    order_cost = order_cost + big_cost
            # cost for lamination
            if 'add_lamin' in request.GET:
                lamin = request.GET['add_lamin']
                if lamin == 'true':
                    lamin_name = request.GET['lamin_name']
                    if frm == "A4":
                        k_lamin = Lamin.objects.get(lamin_name = lamin_name).price_a4
                    elif frm == "A3":
                        k_lamin = Lamin.objects.get(lamin_name = lamin_name).price_a3
                    lamin_cost = number_of_lists * k_lamin
                    order_cost = order_cost + lamin_cost
            # over cost for A4+ or A3+
            if format == "A4p" or format == "A3p":
                k_format = qrk[0]['k_format']
                order_cost = order_cost * k_format
            order_cost = round(order_cost, 2)
            # sends different params (with or without bigovka and lamination)
            if big == 'true' and lamin == 'false':
                params = {"order_cost" : order_cost, "print_cost" : print_cost, "slice_cost":slice_cost, "slices" : slices, "big_cost":big_cost, "big_align":big_align, "big_count":big_count}
            elif lamin == 'true' and big == 'false':
                params = {"order_cost" : order_cost, "print_cost" : print_cost, "slice_cost":slice_cost, "slices" : slices, "lamin_cost":lamin_cost, "lamin_name":lamin_name}
            elif lamin == 'true' and big == 'true':
                params = {"order_cost" : order_cost, "print_cost" : print_cost, "slice_cost":slice_cost, "slices" : slices, "big_cost":big_cost, "big_align":big_align, "big_count":big_count, "lamin_cost":lamin_cost, "lamin_name":lamin_name}
            else:
                params = {"order_cost" : order_cost, "print_cost" : print_cost, "slice_cost":slice_cost, "slices" : slices}
            json = simplejson.dumps(params, indent = 4)
            return HttpResponse(json, mimetype='application/json')
        else:
            return render_to_response('digit.html')
#    except:
#        params = {"Error" : "Oops something wrong."}
#        json = simplejson.dumps(params)
#        return HttpResponse(json, mimetype='application/json', status=406)

# ----------------------------------------------- store orders and sends mails
def add_order(request):
#    try:
        if 'slices' and 'add_lamin' and 'add_big' and 'format' and 'email' and 'On_paper' and 'print_cost' and 'slice_cost' and 'chroma' and 'finally_production' and 'hei_a3' and 'height' and 'number_of_lists' and 'order_cost' and 'quant' and 'time' and 'type' and 'wid_a3' and 'width' in request.GET and request.GET['print_cost'] and request.GET['On_paper'] and request.GET['slice_cost'] and request.GET['format'] and request.GET['slices'] and request.GET['chroma'] and request.GET['finally_production'] and request.GET['hei_a3'] and request.GET['height'] and request.GET['number_of_lists'] and request.GET['order_cost'] and request.GET['quant'] and request.GET['time'] and request.GET['type'] and request.GET['wid_a3'] and request.GET['width']:
            # email of consumer
            if 'email' in request.GET and request.GET['email']:
                emails = request.GET['email']
            elif 'email' in request.GET :
                emails = 'nomail@mail.com'
            email_maker = Constants.objects.get(pk=1).email # from db get mail of Lab01)
            dt = datetime.datetime.now() # get date time
            format = "%d-%m-%y %H:%M" # format it
            dd = dt.strftime(format)
            add_lamin = request.GET['add_lamin'] # get using lamin or not
            add_big = request.GET['add_big'] # same for bigovka
            file = request.GET['file']
            filepath = "/home/lab01/webapps/lab01calc/lab01calc/public/static/uploads/" + file
            # sends to db different params (with or without lamination and bigovka)
            # with bigovka and lamination
            if ('big_cost' and 'big_align' and 'big_count' and 'lamin_cost' and 'lamin_name' in request.GET and request.GET['big_cost'] and request.GET['big_align'] and request.GET['big_count'] and request.GET['lamin_cost'] and request.GET['lamin_name']) and (add_lamin == 'true' and add_big == 'true'):
                qr = Order(date = dd, email = emails, layout = request.GET['layout'], big_cost = float(request.GET['big_cost']), big_align = request.GET['big_align'], big_count = int(request.GET['big_count']), lamin_cost = request.GET['lamin_cost'], lamin_name = request.GET['lamin_name'],  paper = request.GET['param_value'], list_format = request.GET['format'], on_paper = int(request.GET['On_paper']), slices = int(request.GET['slices']), slice_cost = float(request.GET['slice_cost']), print_cost = float(request.GET['print_cost']), chroma = int(request.GET['chroma']), finally_production = int(request.GET['finally_production']), h_list = int(request.GET['hei_a3']), height = float(request.GET['height']), number_of_lists = int(request.GET['number_of_lists']), order_cost = float(request.GET['order_cost']), quant = int(request.GET['quant']), time = int(request.GET['time']), type = request.GET['type'], w_list = int(request.GET['wid_a3']), width = float(request.GET['width']))
                qrbig_cost = qr.big_cost
                qrbig_count = qr.big_count
                qrlamin_cost = qr.lamin_cost
                if qr.big_align == 'vertical': qrbig_align = 'Вертикальная'
                elif qr.big_align == 'horizontal': qrbig_align = 'Горизонтальная'
                if qr.lamin_name == 'gl130': qrlamin_name = 'Глянцевая 130'
                elif qr.lamin_name == 'gl175': qrlamin_name = 'Глянцевая 175'
                elif qr.lamin_name == 'mt125': qrlamin_name = 'Матовая 125'
            # with bigovka, not lamination
            elif ('big_cost' and 'big_align' and 'big_count' in request.GET and request.GET['big_cost'] and request.GET['big_align'] and request.GET['big_count']) and (add_big == 'true' and add_lamin == 'false'):
                qr = Order(date = dd, email = emails, layout = request.GET['layout'],  big_cost = float(request.GET['big_cost']), big_align = request.GET['big_align'], big_count = int(request.GET['big_count']), paper = request.GET['param_value'], list_format = request.GET['format'], on_paper = int(request.GET['On_paper']), slices = int(request.GET['slices']), slice_cost = float(request.GET['slice_cost']), print_cost = float(request.GET['print_cost']), chroma = int(request.GET['chroma']), finally_production = int(request.GET['finally_production']), h_list = int(request.GET['hei_a3']), height = float(request.GET['height']), number_of_lists = int(request.GET['number_of_lists']), order_cost = float(request.GET['order_cost']), quant = int(request.GET['quant']), time = int(request.GET['time']), type = request.GET['type'], w_list = int(request.GET['wid_a3']), width = float(request.GET['width']))
                qrbig_cost = qr.big_cost
                qrbig_count = qr.big_count
                if qr.big_align == 'vertical': qrbig_align = 'Вертикальная'
                elif qr.big_align == 'horizontal': qrbig_align = 'Горизонтальная'
                qrlamin_cost = 'нет'
                qrlamin_name = 'нет'
            # with lamination, not bigovka
            elif ('lamin_cost' and 'lamin_name' in request.GET and request.GET['lamin_cost'] and request.GET['lamin_name']) and (add_big == 'false' and add_lamin == 'true'):
                qr = Order(date = dd, email = emails, layout = request.GET['layout'], lamin_cost = request.GET['lamin_cost'], lamin_name = request.GET['lamin_name'], paper = request.GET['param_value'], list_format = request.GET['format'], on_paper = int(request.GET['On_paper']), slices = int(request.GET['slices']), slice_cost = float(request.GET['slice_cost']), print_cost = float(request.GET['print_cost']), chroma = int(request.GET['chroma']), finally_production = int(request.GET['finally_production']), h_list = int(request.GET['hei_a3']), height = float(request.GET['height']), number_of_lists = int(request.GET['number_of_lists']), order_cost = float(request.GET['order_cost']), quant = int(request.GET['quant']), time = int(request.GET['time']), type = request.GET['type'], w_list = int(request.GET['wid_a3']), width = float(request.GET['width']))
                qrlamin_cost = qr.lamin_cost
                if qr.lamin_name == 'gl130': qrlamin_name = 'Глянцевая 130'
                elif qr.lamin_name == 'gl175': qrlamin_name = 'Глянцевая 175'
                elif qr.lamin_name == 'mt125': qrlamin_name = 'Матовая 125'
                qrbig_align = 'нет'
                qrbig_cost = 'нет'
                qrbig_count = 'нет'
            # without
            elif add_lamin == 'false' and add_big == 'false':
                qr = Order(date = dd, email = emails, layout = request.GET['layout'], paper = request.GET['param_value'], list_format = request.GET['format'], on_paper = int(request.GET['On_paper']), slices = int(request.GET['slices']), slice_cost = float(request.GET['slice_cost']), print_cost = float(request.GET['print_cost']), chroma = int(request.GET['chroma']), finally_production = int(request.GET['finally_production']), h_list = int(request.GET['hei_a3']), height = float(request.GET['height']), number_of_lists = int(request.GET['number_of_lists']), order_cost = float(request.GET['order_cost']), quant = int(request.GET['quant']), time = int(request.GET['time']), type = request.GET['type'], w_list = int(request.GET['wid_a3']), width = float(request.GET['width']))
                qrbig_cost = 'нет'
                qrbig_align = 'нет'
                qrbig_count = 'нет'
                qrlamin_cost = 'нет'
                qrlamin_name = 'нет'
            qr.save()
    #        f = open('/home/lab01calc/lab01calc/public/Temp/working.txt')
    #        c = storage.DropboxFile(f, 'app_folder', '/home/lab01calc/lab01calc/public/Temp/')
    #        sess = session.DropboxSession(APP_KEY, APP_SECRET, ACCESS_TYPE)

    #        request_token = sess.obtain_request_token()

    #        url = sess.build_authorize_url(request_token)
    #        access_token = sess.obtain_access_token(request_token)
    #        clienter = client.DropboxClient(sess)
    #        email_to_order = EmailMessage('Полиграфический калькулятор', 'Ваш заказ принят! Спасибо', email_maker, [emails])
    #        email_to_order.send()


    #        f = open('/home/lab01calc/lab01calc/public/Temp/working-draft.txt')
    #        response = clienter.put_file('/magnum-opus.txt', f)
            # email to maker

    #        json_email = simplejson.loads({"Дата заказа" : qr.date, "Пошта заказчика" : qr.email, "Полная продукция": qr.all, "Полезная продукция":qr.real, "Отход":qr.out, "Изделий на листе":qr.on_paper, "Цветность":qr.chroma, "Всех изделий":qr.finally_production, "Ширина запечатываемого листа":qr.w_list, "Высота запечатываемого листа":qr.h_list, "Ширина изделия":qr.width, "Высота изделия":qr.height, "Количество листов":qr.number_of_lists, "Количетво изделий":qr.quant, "Время на выполнения":qr.time, "Тип полиграфии":qr.type, "Стоимость заказа":qr.order_cost}, encoding='ascii')
    #        json_email = simplejson.dumps({u"Заказ №": qr.id, u"Дата заказа" : qr.date, u"Пошта заказчика" : qr.email, u"Полная продукция": qr.all, u"Полезная продукция":qr.real, u"Отход":qr.out, u"Изделий на листе":qr.on_paper, u"Цветность":qr.chroma, u"Всех изделий":qr.finally_production, u"Ширина запечатываемого листа":qr.w_list, u"Высота запечатываемого листа":qr.h_list, u"Ширина изделия":qr.width, u"Высота изделия":qr.height, u"Количество листов":qr.number_of_lists, u"Количетво изделий":qr.quant, u"Время на выполнения":qr.time, u"Тип полиграфии":qr.type, u"Стоимость заказа":qr.order_cost}, ensure_ascii=False, indent=4, encoding='utf-8')
            # context vars for mails
            qrid = qr.id
            qrdate = qr.date
            qremail = qr.email
            qrslices = qr.slices
            qron_paper = qr.on_paper
            if qr.list_format == 'A4p':
                qrlist_format = 'A4+'
            elif qr.list_format == 'A3p':
                qrlist_format = 'A3+'
            else:
                qrlist_format = qr.list_format
            qrprint_cost = qr.print_cost
            qrslice_cost = qr.slice_cost
            if qr.chroma == 10: qrchroma = '1+0'
            elif qr.chroma == 11: qrchroma = '1+1'
            elif qr.chroma == 40: qrchroma = '4+0'
            elif qr.chroma == 44: qrchroma = '4+4'
            else: qrchroma = qr.chroma
            qrfinally_production = qr.finally_production
            qrh_list = qr.h_list
            qrheight = qr.height
            qrnumber_of_lists = qr.number_of_lists
            qrorder_cost = qr.order_cost
            qrquant = qr.quant
            qrtime = qr.time
            qrw_list = qr.w_list
            qrwidth = qr.width
            if qr.type == 'digit':
                qrtype = 'Цифровая'
            elif qr.type == 'offset':
                qrtype = 'Офсетная'
            elif qr.type == 'wide':
                qrtype = 'Широкоформатная'
            else:
                qrtype = qr.type
            ident = request.GET['param_value']
            qrpaper = Paper_params.objects.get(param_value = ident).param_name
            from django.conf import  settings
            MEDIA_URL = settings.MEDIA_URL
            # mail to lab01
            plaintext = get_template('email_order.txt')
            htmly     = get_template('email_order.html')
            rendr = Context({"qrid" : qrid, "qrchroma" : qrchroma, "qrbig_cost" : qrbig_cost, "qrbig_align" : qrbig_align, "qrbig_count" : qrbig_count, "qrlamin_cost" : qrlamin_cost, "qrlamin_name" : qrlamin_name, "qrpaper" : qrpaper, "qrdate" : qrdate, "qremail" : qremail, "qrlist_format": qrlist_format, "qrslices":qrslices, "qrprint_cost":qrprint_cost, "qrslice_cost":qrslice_cost, "qron_paper":qron_paper, "qrchroma":qrchroma, "qrfinally_production":qrfinally_production, "qrw_list":qrw_list, "qrh_list":qrh_list, "qrwidth":qrwidth, "qrheight":qrheight, "qrnumber_of_lists":qrnumber_of_lists, "qrquant":qrquant, "qrtime":qrtime, "qrtype":qrtype, "qrorder_cost":qrorder_cost })
            subject, from_email, to = 'Новый заказ от полиграфического калькулятора', email_maker, emails
            text_content = plaintext.render(rendr)
            html_content = htmly.render(rendr)
            msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
            msg.attach_file(filepath)
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            # mail to замовник
            plaintext = get_template('email.txt')
            htmly     = get_template('email.html')
            rendr = Context({"qrid" : qrid, "qrpaper" : qrpaper, "qrdate" : qrdate, "qremail" : qremail, "qrlist_format": qrlist_format, "qrslices":qrslices, "qrprint_cost":qrprint_cost, "qrslice_cost":qrslice_cost, "qron_paper":qron_paper, "qrchroma":qrchroma, "qrfinally_production":qrfinally_production, "qrw_list":qrw_list, "qrh_list":qrh_list, "qrwidth":qrwidth, "qrheight":qrheight, "qrnumber_of_lists":qrnumber_of_lists, "qrquant":qrquant, "qrtime":qrtime, "qrorder_cost":qrorder_cost, "qrtype":qrtype, "MEDIA_URL":MEDIA_URL })
            subject, from_email, to = 'Новый заказ от полиграфического калькулятора', email_maker, emails
            text_content = plaintext.render(rendr)
            html_content = htmly.render(rendr)
            msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            json = simplejson.dumps({"Order":qrid})
            return HttpResponse(json, mimetype='application/json')
        else:
            json = simplejson.dumps({"No parameters" : "were send"})
            return HttpResponse(json, mimetype='application/json', status=406)
#    except:
#        json = simplejson.dumps({"Something wrong" : "or error were occured"})
#        return HttpResponse(json, mimetype='application/json', status=406)

# ------------------------------------------------------get all formats
def paper_size(request):
    try:
        params = {'Formats' : list(Size_paper.objects.values('name', 'width', 'height').order_by('id'))}
        json = simplejson.dumps(params, ensure_ascii=False, indent=4)
        return HttpResponse(json, mimetype='application/json; charset=utf-8')
    except:
        params = {"Oops something wrong." : "Error"}
        json = simplejson.dumps(params)
        return HttpResponse(json, mimetype='application/json', status=406)

# ---------------------------------------------------get all type of lamination
def lamin(request):
    try:
        params = {'Lamins' : list(Lamin.objects.values('lamin_label', 'lamin_name'))}
        json = simplejson.dumps(params, ensure_ascii=False, indent=4)
        return HttpResponse(json, mimetype='application/json; charset=utf-8')
    except:
        params = {"Oops something wrong." : "Error"}
        json = simplejson.dumps(params)
        return HttpResponse(json, mimetype='application/json', status=406)

# ------------------------------------------------------------file upload



from ajaxuploader.views import AjaxFileUploader


def start(request):
    csrf_token = get_token(request)
    return render_to_response('home.html',
            {'csrf_token': csrf_token}, context_instance = RequestContext(request))

import_uploader = AjaxFileUploader()
#----------------------------------------------------- login and logout


def login(request):
    username = request.POST['username']
    password = request.POST['password']
    user = auth.authenticate(username=username, password=password)
    if user is not None and user.is_active:
        log = True
        # good password and user is active
        auth.login(request, user)
        # redirecting
        return render(request, "home.html", Context({"is_log":log}))
    else:
        log = False
        # show error page
        return render(request, "home.html", Context({"is_log":log}))

def logout(request):
    auth.logout(request)
    #
    return render(request, "home.html")