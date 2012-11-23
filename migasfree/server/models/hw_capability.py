# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _

from migasfree.server.models import HwNode


class HwCapability(models.Model):
    node = models.ForeignKey(
        HwNode,
        verbose_name=unicode(_("hardware node"))
    )

    name = models.TextField(
        unicode(_("name")),
        null=False,
        blank=True
    )  # This is the field "capability" in lshw

    description = models.TextField(
        unicode(_("description")),
        null=True,
        blank=True
    )

    def __unicode__(self):
        return u'%s' % (self.name)

    class Meta:
        app_label = 'server'
        verbose_name = unicode(_("Hardware Capability"))
        verbose_name_plural = unicode(_("Hardware Capabilities"))
        unique_together = (("name", "node"),)
