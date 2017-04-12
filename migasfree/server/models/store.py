# -*- coding: utf-8 -*-

import os
import shutil

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext, ugettext_lazy as _
from django.utils.text import slugify
from django.core.urlresolvers import reverse
from django.conf import settings
from django.db.models.signals import pre_delete
from django.dispatch import receiver

from . import Project, MigasLink


class StoreManager(models.Manager):
    def create(self, name, project):
        obj = Store()
        obj.name = name
        obj.project = project
        obj.save()

        return obj

    def by_project(self, project_id):
        return self.get_queryset().filter(project__id=project_id)


@python_2_unicode_compatible
class Store(models.Model, MigasLink):
    """
    Location where packages will be stored (p.e. /debian8/third/syntevo/)
    """

    name = models.CharField(
        verbose_name=_("name"),
        max_length=50
    )

    project = models.ForeignKey(
        Project,
        verbose_name=_("project")
    )

    objects = StoreManager()

    @staticmethod
    def path(project_name, name):
        return os.path.join(
            settings.MIGASFREE_REPO_DIR,
            project_name,
            'STORES',
            name
        )

    def menu_link(self):
        if self.id:
            info_link = reverse(
                'package_info',
                args=('%s/STORES/%s/' % (self.project.name, self.name),)
            )

            download_link = '%s%s/STORES/%s/' % (
                settings.MEDIA_URL,
                self.project.name,
                self.name
            )

            self._actions = [
                [ugettext('Package Information'), info_link],
                [ugettext('Download'), download_link]
            ]

        return super(Store, self).menu_link()

    def _create_dir(self):
        path = self.path(self.project.name, self.name)
        if not os.path.exists(path):
            os.makedirs(path)

    def save(self, *args, **kwargs):
        self.name = slugify(self.name)
        self._create_dir()

        super(Store, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        app_label = 'server'
        verbose_name = _('Store')
        verbose_name_plural = _('Stores')
        unique_together = (('name', 'project'),)
        permissions = (("can_save_store", "Can save Store"),)
        ordering = ['name', 'project']


@receiver(pre_delete, sender=Store)
def delete_store(sender, instance, **kwargs):
    path = Store.path(instance.project.name, instance.name)
    if os.path.exists(path):
        shutil.rmtree(path)
