# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _

from . import HwNode


class HwConfigurationManager(models.Manager):
    def create(self, node, name, value):
        obj = HwConfiguration(
            node=node,
            name=name,
            value=value
        )
        obj.save()

        return obj


class HwConfiguration(models.Model):
    node = models.ForeignKey(
        HwNode,
        verbose_name=_("hardware node")
    )

    name = models.TextField(
        verbose_name=_("name"),
        null=False,
        blank=True
    )  # This is the field "config" in lshw

    value = models.TextField(
        verbose_name=_("value"),
        null=True,
        blank=True
    )

    objects = HwConfigurationManager()

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = 'server'
        verbose_name = _("Hardware Capability")
        verbose_name_plural = _("Hardware Capabilities")
        unique_together = (("name", "node"),)
