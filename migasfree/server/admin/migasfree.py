# -*- coding: utf-8 -*-

from django.utils.translation import ugettext

from import_export.admin import ExportActionModelAdmin
from django.contrib.admin.views.main import ChangeList
from django.utils.translation import ugettext_lazy as _
from django.db.models.fields import BooleanField, IntegerField


class MigasAdmin(ExportActionModelAdmin):
    list_display_links = None
    filter_description = ""

    @staticmethod
    def boolean_field(field):
        style = 'fa-check boolean-yes'
        text = ugettext('Yes')
        if not field:
            style = 'fa-times boolean-no'
            text = ugettext('No')

        return '<span class="fa %s"><span class="sr-only">%s</span></span>' % (
            style, text
        )

    def get_changelist(self, request, **kwargs):
        return MigasChangeList


class MigasChangeList(ChangeList):
    def __init__(self, *args, **kwargs):
        super(MigasChangeList, self).__init__(*args, **kwargs)
        self.filter_description = []
        for x in self.filter_specs:
            if hasattr(x, 'lookup_choices') \
                    and hasattr(x, 'used_parameters') and x.used_parameters:
                if isinstance(x.lookup_choices[0][0], int):
                    try:
                        element = dict(
                            x.lookup_choices
                        )[int(x.used_parameters.values()[0])]
                    except:
                        element = ""
                        for key, value in x.used_parameters.iteritems():
                            element += "%s=%s " % (key.split("__")[1], value)
                else:
                    element = dict(
                        x.lookup_choices
                    )[x.used_parameters.values()[0]]

                self.append(x.title, element)
            elif hasattr(x, 'lookup_choices') and hasattr(x, "lookup_val") \
                    and x.lookup_val:
                if isinstance(x.lookup_choices[0][0], int):
                    self.append(
                        x.lookup_title,
                        dict(x.lookup_choices)[int(x.lookup_val)]
                    )
                else:
                    self.append(
                        x.lookup_title,
                        dict(x.lookup_choices)[x.lookup_val]
                    )
            elif hasattr(x, 'links'):
                for l in x.links:
                    if l[1] == x.used_parameters:
                        self.append(x.title, unicode(l[0]))
                        break
            elif hasattr(x, 'field') and hasattr(x.field, 'choices') \
                    and hasattr(x, 'lookup_val') and x.lookup_val:
                if isinstance(x.field, BooleanField):
                    if x.lookup_val == "0":
                        self.append(x.title, _("No"))
                    else:
                        self.append(x.title, _("Yes"))
                elif isinstance(x.field, IntegerField):
                    elements = []
                    for element in x.lookup_val.split(','):
                        elements.append(
                            unicode(dict(x.field.choices)[int(element)])
                        )
                    self.append(x.title, ", ".join(elements))
                else:
                    elements = []
                    for element in x.lookup_val.split(','):
                        elements.append(unicode(dict(x.field.choices)[element]))
                    self.append(x.title, ", ".join(elements))

        _filter = ", ".join(u"%s: %s" % (
               k["name"].capitalize(),
               unicode(k["value"]))
               for k in self.filter_description)
        if _filter:
            _filter = "(%s)" % _filter
        self.title = u"%s %s" % (
           self.model._meta.verbose_name_plural,
           _filter
        )

    def append(self, name, val):
        self.filter_description.append({"name": unicode(name), "value": val})