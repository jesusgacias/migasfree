# -*- coding: UTF-8 -*-

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist


@login_required
def link(request):
    _app = request.GET.get('app', 'server')
    _model = request.GET.get('model', None)
    _pk = request.GET.get('pk', None)

    try:
        obj_link = apps.get_model(_app, _model).objects.get(pk=_pk).menu_link()
    except ObjectDoesNotExist as e:
        return HttpResponse(e)

    return HttpResponse(obj_link)