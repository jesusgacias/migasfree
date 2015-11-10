# -*- coding: utf-8 *-*

from django.db import models
from django.utils.translation import ugettext_lazy as _

from .computer import Computer


class StatusLogManager(models.Manager):
    def create(self, computer):
        sl = StatusLog()
        sl.computer = computer
        sl.status = computer.status
        sl.save()

        return sl


class StatusLog(models.Model):
    computer = models.ForeignKey(
        Computer,
        verbose_name=_("computer"),
    )

    status = models.CharField(
        verbose_name=_('status'),
        max_length=20,
        null=False,
        choices=Computer.STATUS_CHOICES,
        default='intended'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('date')
    )

    objects = StatusLogManager()

    def __unicode__(self):
        return '%s - %s' % (self.computer.__unicode__(), self.status)

    def computer_link(self):
        return self.computer.link()

    computer_link.allow_tags = True
    computer_link.short_description = _("Computer")

    class Meta:
        app_label = 'server'
        verbose_name = _("Status Log")
        verbose_name_plural = _("Status Logs")
        permissions = (("can_save_statuslog", "Can save Status Log"),)
