# -*- coding: utf-8 -*-

import os

from django.core.urlresolvers import reverse
from django.utils.html import format_html

from migasfree.server.functions import trans

# Programming Language for Properties and FaultDefs
LANGUAGES_CHOICES = (
    (0, 'bash'),
    (1, 'python'),
    (2, 'perl'),
    (3, 'php'),
    (4, 'ruby'),
    (5, 'cmd'),
)


class MigasLink(object):
    _actions = None

    def link(self):
        _link = '<span class="sr-only">%s</span><a href="%s" class="btn btn-xs">%s</a>' % (
            self.__unicode__(),
            reverse(
                'admin:server_%s_change' % self._meta.model_name,
                args=(self.id, )
            ),
            self.__unicode__()
        )

        _link += '<button type="button" ' + \
            'class="btn btn-default dropdown-toggle" data-toggle="dropdown">' + \
            '<span class="caret"></span>' + \
            '<span class="sr-only">' + trans("Toggle Dropdown") + \
            '</span></button>'

        related_data = ''
        if self._actions is not None:
            related_data += '<li role="presentation" class="dropdown-header">%s</li>' % trans("Actions")
            for item in self._actions:
                related_data += '<li><a href="%(href)s">%(protocol)s</a></li>' % {
                    'href': item[1],
                    'protocol': item[0]
                }

            related_data += '<li role="presentation" class="divider"></li>'

        related_data += '<li role="presentation" class="dropdown-header">%s</li>' % trans("Related data")
        related_objects = self._meta.get_all_related_objects_with_model() + self._meta.get_all_related_m2m_objects_with_model()
        for related_object, _ in related_objects:
            try:
                related_link = reverse(
                    'admin:server_%s_changelist' % related_object.model._meta.model_name
                )
                related_data += '<li><a href="%s?%s__exact=%d">%s</a></li>' % (
                    related_link,
                    related_object.field.name,
                    self.id,
                    trans(related_object.model._meta.verbose_name_plural)
                )
            except:
                pass

        return format_html(
            '<div class="btn-group btn-group-xs">' + \
            _link + '<ul class="dropdown-menu" role="menu">' + \
            related_data + '</ul></div>'
        )

    link.allow_tags = True
    link.short_description = ''
