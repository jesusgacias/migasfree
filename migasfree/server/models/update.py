# -*- coding: utf-8 -*-

from django.db import models
from django.utils import timezone, dateformat
from django.utils.translation import ugettext_lazy as _

from . import Computer, Version, User, MigasLink


class UpdateManager(models.Manager):
    def create(self, computer):
        obj = Update()
        obj.computer = computer
        obj.version = computer.version
        obj.user = computer.login().user
        obj.date = dateformat.format(timezone.now(), 'Y-m-d H:i:s')
        obj.save()

        return obj


class Update(models.Model, MigasLink):
    computer = models.ForeignKey(
        Computer,
        verbose_name=_("computer")
    )

    user = models.ForeignKey(
        User,
        verbose_name=_("user")
    )

    version = models.ForeignKey(
        Version,
        verbose_name=_("version"),
        null=True
    )

    date = models.DateTimeField(
        verbose_name=_("date"),
        default=0
    )

    objects = UpdateManager()

    def save(self, *args, **kwargs):
        super(Update, self).save(*args, **kwargs)

        #update last update in computer
        self.computer.datelastupdate = self.date
        self.computer.save()

    def __unicode__(self):
        return u'%s-%s' % (self.computer.__unicode__(), self.date)

    def computer_link(self):
        return self.computer.link()

    computer_link.allow_tags = True
    computer_link.short_description = _("Computer")

    class Meta:
        app_label = 'server'
        verbose_name = _("Update")
        verbose_name_plural = _("Updates")
        permissions = (("can_save_update", "Can save Update"),)
