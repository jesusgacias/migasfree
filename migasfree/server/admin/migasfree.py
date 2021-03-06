# -*- coding: utf-8 -*-

import inspect
import datetime

from import_export.admin import ExportActionModelAdmin
from django.contrib.admin.views.main import ChangeList
from django.utils.translation import ugettext, ugettext_lazy as _
from django.utils.html import format_html
from django.db.models.fields import BooleanField, IntegerField
from django.apps import apps
from django.template.loader import render_to_string


class MigasFields(object):
    @staticmethod
    def boolean(name="", description='', model=None):
        def getter(self, obj):
            style = 'fa-check boolean-yes'
            text = ugettext('Yes')
            if not getattr(obj, name):
                style = 'fa-times boolean-no'
                text = ugettext('No')

            html = '<span class="fas %s"></span><span class="sr-only">%s</span>'

            return format_html(html % (style, text))

        getter.admin_order_field = name

        getter.short_description = description \
            or _(model._meta.get_field(name).verbose_name)

        return getter

    @staticmethod
    def text(model=None, name="", description=''):
        def getter(self, obj):
            return format_html(getattr(obj, name))

        getter.admin_order_field = name

        getter.short_description = description \
            or _(model._meta.get_field(name).verbose_name)

        return getter

    @staticmethod
    def link(name='', model=None, description=None, order=None):
        """
        Create a function that can be attached to a ModelAdmin to use
        as a list_display field
        """
        related_names = name.split('__')

        def getter(self, obj):
            for item in related_names:
                target = getattr(obj, item)
                if not (
                    isinstance(target, unicode)
                    or isinstance(target, datetime.datetime)
                    or target is None
                ):
                    obj = target
                else:
                    if target is None:
                        return ""

                if inspect.ismethod(obj):  # Is a method
                    obj = obj()

            return obj.link()

        getter.admin_order_field = order or name

        for related_name in related_names:
            if hasattr(model, "_meta"):
                try:
                    field = model
                    model = model._meta.get_field(related_name)
                    if model.get_internal_type() == "ForeignKey":
                        model = model.related_model
                        getter.short_description = description \
                            or _(model._meta.verbose_name.title())
                    else:
                        getter.short_description = description \
                            or _(field._meta.verbose_name.title())
                except:
                    pass

        return getter

    @staticmethod
    def objects_link(name='', description=None, model=None):
        """
        Create a function that can be attached to a ModelAdmin to use
        as a list_display field
        """
        related_names = name.split('__')

        def getter(self, obj):
            if not related_names[0]:
                return obj.link()

            for item in related_names:
                obj = getattr(obj, item)

            if inspect.ismethod(obj):  # Is a method
                obj = obj()

            if not hasattr(obj, 'all'):
                return obj.link()

            return format_html(
                render_to_string(
                    'includes/objects_link.html',
                    {
                        'objects': obj.all()
                    }
                )
            )

        for related_name in related_names:
            field = model
            if hasattr(model, "_meta"):
                related_name = related_name.replace("_set", "")
                if related_name in model._meta.fields_map:
                    model = model._meta.fields_map[related_name]
                elif inspect.ismethod(model):  # Is a method
                    getter.short_description = description \
                        or getattr(model, related_name).short_description
                    return getter
                else:

                    if inspect.ismethod(getattr(model, related_name)):
                        getter.short_description = description \
                            or getattr(model, related_name).short_description
                        return getter

                    else:
                        model = getattr(model, related_name).field
                        getter.short_description = description \
                            or _(model.verbose_name.title())
                        return getter

                if model.get_internal_type() in [
                    "ForeignKey", "ManyToManyField"
                ]:
                    model = model.related_model
                    getter.short_description = description \
                        or _(model._meta.verbose_name_plural.title())
                else:
                    getter.short_description = description \
                        or _(field._meta.verbose_name_plural.title())

        return getter

    @staticmethod
    def timeline():
        def getter(self, obj):
            if obj.schedule:
                return format_html(
                    render_to_string(
                        'includes/deployment_timeline.html',
                        {
                            'timeline': obj.timeline()
                        }
                    )
                )
            else:
                return ""

        getter.short_description = _("time line")

        return getter


class MigasAdmin(ExportActionModelAdmin):
    list_display_links = None
    filter_description = ''

    def get_changelist(self, request, **kwargs):
        return MigasChangeList

    def get_form(self, request, obj=None, **kwargs):
        form = super(MigasAdmin, self).get_form(request, obj, **kwargs)
        for field in form.base_fields.keys():
            form.base_fields[field].widget.can_change_related = False
            form.base_fields[field].widget.can_add_related = False
            form.base_fields[field].widget.can_delete_related = False

        return form


class MigasChangeList(ChangeList):
    def __init__(self, *args, **kwargs):
        super(MigasChangeList, self).__init__(*args, **kwargs)
        self.filter_description = []
        params = dict(self.params)

        for x in self.filter_specs:
            if hasattr(x, 'lookup_choices') \
                    and hasattr(x, 'used_parameters') and x.used_parameters:
                if hasattr(x, 'lookup_val') and not x.lookup_val:
                    element = ''
                    for key, value in x.used_parameters.iteritems():
                        lookup_type = key.split('__')[1]
                        if lookup_type == 'isnull':
                            element += u'{}'.format(_('empty') if value else _('not empty'))
                        else:
                            element += u'{}={}'.format(lookup_type, value)
                        params.pop(key, None)
                    self.append(x.title, element)
                    break

                if isinstance(x.lookup_choices[0][0], int):
                    element = dict(
                        x.lookup_choices
                    )[int(x.used_parameters.values()[0])]
                else:
                    element = dict(
                        x.lookup_choices
                    )[x.used_parameters.values()[0]]
                self.append(x.title, element)
                for element in x.used_parameters:
                    params.pop(element, None)
            elif hasattr(x, 'lookup_choices') and hasattr(x, 'lookup_val') \
                    and x.lookup_val:
                if isinstance(x.lookup_choices[0][0], int):
                    self.append(
                        x.lookup_title,
                        dict(x.lookup_choices)[int(x.lookup_val)]
                    )
                    params.pop(x.lookup_kwarg, None)
                else:
                    self.append(
                        x.lookup_title,
                        dict(x.lookup_choices)[x.lookup_val]
                    )
                    params.pop(x.lookup_kwarg, None)
            elif hasattr(x, 'links'):
                for l in x.links:
                    if l[1] == x.used_parameters:
                        self.append(x.title, unicode(l[0]))
                        break
            elif hasattr(x, 'field') and hasattr(x.field, 'choices') \
                    and hasattr(x, 'lookup_val') and x.lookup_val:
                if isinstance(x.field, BooleanField):
                    if x.lookup_val == '0':
                        self.append(x.title, _("No"))
                        params.pop(x.lookup_kwarg, None)
                    else:
                        self.append(x.title, _("Yes"))
                        params.pop(x.lookup_kwarg, None)
                elif isinstance(x.field, IntegerField):
                    elements = []
                    for element in x.lookup_val.split(','):
                        elements.append(
                            unicode(dict(x.field.choices)[int(element)])
                        )
                    self.append(x.title, ', '.join(elements))
                    params.pop(x.lookup_kwarg, None)
                else:
                    elements = []
                    for element in x.lookup_val.split(','):
                        elements.append(unicode(dict(x.field.choices)[element]))
                        params.pop(x.lookup_kwarg, None)
                    self.append(x.title, ', '.join(elements))
                    params.pop(x.lookup_kwarg, None)

        # filters no standards
        params.pop("date__gte", None)
        params.pop("date__lt", None)
        for k in params:
            if k.endswith("__id__exact"):
                _classname = k.split("__")[0]
                _name = ugettext(_classname.capitalize())

                if _classname == "ExcludeAttribute":
                    _classname = "deployment"
                    _name = "excluded attributes"
                if _classname == "ExcludedAttributesGroup":
                    _classname = "attributeset"
                    _name = "excluded attributes"
                if _classname == 'sync_attributes':
                    _classname = 'attribute'
                    _name = 'sync attributes'
                if _classname == 'included_attributes':
                    _classname = 'attribute'
                    _name = 'included attributes'
                if _classname == 'excluded_attributes':
                    _classname = 'attribute'
                    _name = 'excluded attributes'

                if not hasattr(self.model, _classname):
                    _app = self.model._meta.app_label
                    model = apps.get_model(_app, _classname)
                    self.append(_name, model.objects.get(pk=params[k]))
                else:
                    model = getattr(self.model, _classname)
                    _classname = model.field.related_model.__name__
                    _app = model.field.related_model._meta.app_label
                    model = apps.get_model(_app, _classname)
                    self.append(_name, model.objects.get(pk=params[k]))

            elif k == "id__in":
                _classname = self.model.__name__
                _app = self.model._meta.app_label
                model = apps.get_model(_app, _classname)
                _list = []
                for _id in params[k].split(",")[0:10]:  # limit to 10 elements
                    _list.append(
                        model.objects.get(
                            pk=int(_id)
                        ).__str__()
                    )
                if len(_list) == 10:
                    self.append(_classname, ", ".join(_list) + "...")
                else:
                    self.append(_classname, ", ".join(_list))

            else:
                self.append(k, params[k])

        _filter = ", ".join(
            u"{}: {}".format(
                k["name"].capitalize(),
                unicode(k["value"])
            )
            for k in self.filter_description
        )
        if _filter:
            _filter = u"({})".format(_filter)

        self.title = u"{} {}".format(
            self.model._meta.verbose_name_plural,
            _filter
        )

    def append(self, name, value):
        self.filter_description.append({
            "name": _(unicode(name)),
            "value": value
        })
