# -*- coding: utf-8 -*-

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django.core.validators import MinValueValidator
from django.db.models import Count

from . import Schedule, Attribute, Login, UserProfile


@python_2_unicode_compatible
class ScheduleDelay(models.Model):
    delay = models.IntegerField(verbose_name=_("delay"))

    schedule = models.ForeignKey(
        Schedule,
        verbose_name=_("schedule")
    )

    attributes = models.ManyToManyField(
        Attribute,
        blank=True,
        verbose_name=_("attributes")
    )

    duration = models.IntegerField(
        verbose_name=_("duration"),
        default=1,
        validators=[MinValueValidator(1), ]
    )

    def total_computers(self):
        version = UserProfile.get_logged_version()
        if version:
            return Login.objects.filter(
                attributes__id__in=self.attributes.all().values_list("id"),
                computer__version_id=version.id
            ).annotate(total=Count('id')).order_by('id').count()
        else:
            return Login.objects.filter(
                attributes__id__in=self.attributes.all().values_list("id")
            ).annotate(total=Count('id')).order_by('id').count()

    total_computers.short_description = _('Total computers')

    def __str__(self):
        return '%s - %s' % (self.schedule.name, str(self.delay))

    def list_attributes(self):
        return ', '.join(
            self.attributes.values_list('value', flat=True).order_by('value')
        )

    list_attributes.short_description = _("attributes")

    class Meta:
        app_label = 'server'
        verbose_name = _("Schedule Delay")
        verbose_name_plural = _("Schedule Delays")
        unique_together = (("schedule", "delay"),)
        permissions = (("can_save_scheduledelay", "Can save Schedule Delay"),)
