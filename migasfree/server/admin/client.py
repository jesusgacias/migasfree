# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import resolve, reverse
from django.contrib import admin, messages
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.shortcuts import redirect, render
from django.utils.translation import ugettext_lazy as _
from django.db.models import Prefetch

from ajax_select import make_ajax_form
from ajax_select.admin import AjaxSelectAdmin

from .migasfree import MigasAdmin, MigasFields

from ..filters import ProductiveFilterSpec, UserFaultFilter
from ..forms import ComputerForm
from ..resources import ComputerResource
from ..models import (
    AutoCheckError, Computer, Error, Fault, FaultDef, Message,
    Migration, Notification, StatusLog, Update, User, DeviceLogical, HwNode
)

admin.site.register(AutoCheckError)


def add_computer_search_fields(fields_list):
    for field in settings.MIGASFREE_COMPUTER_SEARCH_FIELDS:
        fields_list.append("computer__%s" % field)

    return tuple(fields_list)


@admin.register(Computer)
class ComputerAdmin(AjaxSelectAdmin, MigasAdmin):
    form = ComputerForm
    list_display = (
        'name_link',
        'status',
        'version_link',
        'sync_user_link',
        'sync_end_date',
        'hw_link',
    )
    ordering = (settings.MIGASFREE_COMPUTER_SEARCH_FIELDS[0],)
    list_filter = (
        'version__name',
        ('status', ProductiveFilterSpec),
        'machine',
    )
    search_fields = settings.MIGASFREE_COMPUTER_SEARCH_FIELDS + (
        'sync_user__name', 'sync_user__fullname'
    )

    readonly_fields = (
        'name',
        'uuid',
        'version_link',
        'created_at',
        'ip_address',
        'software_inventory',
        'software_history',
        'hw_link',
        'machine',
        'cpu',
        'ram',
        'storage',
        'disks',
        'mac_address',
        'logical_devices_link',
        'sync_user_link',
        'sync_attributes_link',
        'sync_start_date',
        'sync_end_date',
        'unchecked_errors',
        'unchecked_faults',
        'last_update_time',
    )

    fieldsets = (
        (_('General'), {
            'fields': (
                'name',
                'version_link',
                'created_at',
                'ip_address',
            )
        }),
        (_('Current Situation'), {
            'fields': (
                'status',
                'sync_user_link',
                'sync_attributes_link',
                'sync_start_date',
                'sync_end_date',
                'last_update_time',
                'unchecked_errors',
                'unchecked_faults',
            )
        }),
        (_('Hardware'), {
            'fields': (
                'last_hardware_capture',
                'hw_link',
                'uuid',
                'machine',
                'cpu',
                'ram',
                'storage',
                'disks',
                'mac_address',
            )
        }),
        (_('Software'), {
            'fields': ('software_inventory', 'software_history',)
        }),
        (_('Devices'), {
            'fields': ('logical_devices_link', 'default_logical_device',)
        }),
        (_('Tags'), {
            'fields': ('tags',)
        }),
    )

    resource_class = ComputerResource
    actions = ['delete_selected', 'change_status']

    def unchecked_errors(self, obj):
        count = Error.unchecked.filter(computer__pk=obj.pk).count()
        if not count:
            return '<span class="label label-default">{}</span>'.format(count)

        return '<a class="label label-danger" ' \
            'href="{}?computer__id__exact={}&checked__exact={}">{}</a>'.format(
                reverse('admin:server_error_changelist'),
                obj.pk,
                0,
                count
            )

    unchecked_errors.short_description = _('Unchecked Errors')
    unchecked_errors.allow_tags = True

    def unchecked_faults(self, obj):
        count = Fault.unchecked.filter(computer__pk=obj.pk).count()
        if not count:
            return '<span class="label label-default">{}</span>'.format(count)

        return '<a class="label label-danger" ' \
            'href="{}?computer__id__exact={}&checked__exact={}">{}</a>'.format(
                reverse('admin:server_fault_changelist'),
                obj.pk,
                0,
                count
            )

    unchecked_faults.short_description = _('Unchecked Faults')
    unchecked_faults.allow_tags = True

    def last_update_time(self, obj):
        is_updating = Message.objects.filter(computer__id=obj.pk).count()
        diff = obj.sync_end_date - obj.sync_start_date

        if is_updating:
            delayed_time = datetime.now() - timedelta(
                0, settings.MIGASFREE_SECONDS_MESSAGE_ALERT
            )
            if obj.sync_start_date < delayed_time:
                return '<span class="label label-warning" title="{}">' \
                    '<i class="fa fa-warning"></i> {}</span>'.format(
                        _('Delayed Computer'),
                        diff
                    )
            else:
                return '<span class="label label-info">' \
                    '<i class="fa fa-refresh"></i> {}</span>'.format(
                        _('Updating...'),
                    )

        return diff

    last_update_time.short_description = _('Last Update Time')
    last_update_time.allow_tags = True

    name_link = MigasFields.link(model=Computer, name="name")
    version_link = MigasFields.link(
        model=Computer, name='version', order='version__name'
    )
    hw_link = MigasFields.objects_link(
        model=Computer, name='hwnode_set', description=_('Product')
    )
    logical_devices_link = MigasFields.objects_link(
        model=Computer, name='logical_devices'
    )
    sync_user_link = MigasFields.link(
        model=Computer, name='sync_user__name', description=_('User'), order="sync_user__name"
    )
    sync_attributes_link = MigasFields.objects_link(model=Computer, name='sync_attributes')

    def delete_selected(self, request, objects):
        if not self.has_delete_permission(request):
            raise PermissionDenied

        return render(
            request,
            'computer_confirm_delete_selected.html',
            {
                'objects': [x.__str__() for x in objects],
                'ids': ', '.join([str(x.id) for x in objects])
            }
        )

    delete_selected.short_description = _("Delete selected "
                                          "%(verbose_name_plural)s")

    def change_status(self, request, objects):
        if not self.has_change_permission(request):
            raise PermissionDenied

        return render(
            request,
            'computer_change_status.html',
            {
                'objects': [x.__str__() for x in objects],
                'ids': ', '.join([str(x.id) for x in objects]),
                'status': Computer.STATUS_CHOICES
            }
        )

    change_status.short_description = _("Change status...")

    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        if db_field.name == "devices_logical":
            kwargs['widget'] = FilteredSelectMultiple(
                db_field.verbose_name,
                (db_field.name in self.filter_vertical)
            )
            return db_field.formfield(**kwargs)

        return super(ComputerAdmin, self).formfield_for_manytomany(
            db_field,
            request,
            **kwargs
        )

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == "default_logical_device":
            args = resolve(request.path).args
            computer = Computer.objects.get(pk=args[0])
            kwargs['queryset'] = DeviceLogical.objects.filter(
                pk__in=[x.id for x in computer.logical_devices()]
            )
        return super(ComputerAdmin, self).formfield_for_foreignkey(
            db_field,
            request,
            **kwargs
        )

    def has_add_permission(self, request):
        return False

    def get_queryset(self, request):
        return super(ComputerAdmin, self).get_queryset(
            request
        ).select_related(
            "version",
            "sync_user",
            "default_logical_device",
            "default_logical_device__feature",
            "default_logical_device__device",
        ).prefetch_related(
            Prefetch('hwnode_set', queryset=HwNode.objects.filter(parent=None)),
        )


@admin.register(Error)
class ErrorAdmin(MigasAdmin):
    list_display = (
        'id',
        'computer_link',
        'version_link',
        'my_checked',
        'date',
        'truncated_error',
    )
    list_display_links = ('id',)
    list_filter = ('checked', 'date', 'version__platform', 'version')
    ordering = ('-date', 'computer',)
    search_fields = add_computer_search_fields(['date', 'error'])
    readonly_fields = ('computer_link', 'version_link', 'date', 'error')
    exclude = ('computer', 'version')
    actions = ['checked_ok']

    my_checked = MigasFields.boolean(model=Error, name='checked')
    computer_link = MigasFields.link(
        model=Error, name='computer', order='computer__name'
    )
    version_link = MigasFields.link(
        model=Error, name="version", order='version__name'
    )

    def truncated_error(self, obj):
        if len(obj.error) <= 250:
            return obj.error
        else:
            return obj.error[:250] + " ..."

    truncated_error.short_description = _("Truncated error")
    truncated_error.admin_order_field = 'error'

    def checked_ok(self, request, queryset):
        for item in queryset:
            item.okay()

        messages.success(request, _('Checked %s') % _('Errors'))

        return redirect(request.get_full_path())

    checked_ok.short_description = _("Checking is O.K.")

    def has_add_permission(self, request):
        return False

    def get_queryset(self, request):
        return super(ErrorAdmin, self).get_queryset(
            request
        ).select_related(
            'version',
            'computer',
        )


@admin.register(Fault)
class FaultAdmin(MigasAdmin):
    list_display = (
        'id',
        'computer_link',
        'version_link',
        'my_checked',
        'date',
        'text',
        'fault_definition_link',
    )
    list_display_links = ('id',)
    list_filter = (
        UserFaultFilter, 'checked', 'date',
        'version__platform', 'version', 'faultdef'
    )
    ordering = ('-date', 'computer',)
    search_fields = add_computer_search_fields(['date', 'faultdef__name'])
    readonly_fields = (
        'computer_link', 'fault_definition_link',
        'version_link', 'date', 'text'
    )
    exclude = ('computer', 'version', 'faultdef')
    actions = ['checked_ok']

    my_checked = MigasFields.boolean(model=Fault, name='checked')
    computer_link = MigasFields.link(
        model=Fault, name='computer', order='computer__name'
    )
    version_link = MigasFields.link(
        model=Fault, name='version', order='version__name'
    )
    fault_definition_link = MigasFields.link(
        model=Fault, name='faultdef', order='faultdef__name'
    )

    def checked_ok(self, request, queryset):
        for item in queryset:
            item.okay()

        messages.success(request, _('Checked %s') % _('Faults'))

        return redirect(request.get_full_path())

    checked_ok.short_description = _("Checking is O.K.")

    def has_add_permission(self, request):
        return False

    def get_queryset(self, request):
        return super(FaultAdmin, self).get_queryset(
            request
        ).select_related(
            'version',
            'faultdef',
            'computer',
        )


@admin.register(FaultDef)
class FaultDefAdmin(MigasAdmin):
    form = make_ajax_form(FaultDef, {'attributes': 'attribute'})
    list_display = ('name_link', 'my_active', 'attributes_link', 'users_link')
    list_filter = ('active', 'users')
    search_fields = ('name',)
    filter_horizontal = ('attributes',)

    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'active', 'language', 'code')
        }),
        (_('Atributtes'), {
            'fields': ('attributes',)
        }),
        (_('Users'), {
            'fields': ('users',)
        }),
    )

    name_link = MigasFields.link(model=FaultDef, name='name')
    my_active = MigasFields.boolean(model=FaultDef, name='active')
    attributes_link = MigasFields.objects_link(
        model=FaultDef, name='attributes'
    )
    users_link = MigasFields.objects_link(model=FaultDef, name='users')

    def get_form(self, request, obj=None, **kwargs):
        form = super(FaultDefAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['users'].widget.can_add_related = False

        return form

    def get_queryset(self, request):
        return super(FaultDefAdmin, self).get_queryset(
            request
            ).prefetch_related(
                'attributes',
                'attributes__property_att',
                'users',
            )


@admin.register(Message)
class MessageAdmin(MigasAdmin):
    list_display = ('id', 'computer_link', 'date', 'text')
    list_display_links = ('id',)
    ordering = ('-date',)
    list_filter = ('date',)
    search_fields = ('computer', 'text', 'date')
    readonly_fields = ('computer_link', 'text', 'date')
    exclude = ('computer',)

    computer_link = MigasFields.link(
        model=Message, name='computer', order='computer__name'
    )


@admin.register(Migration)
class MigrationAdmin(MigasAdmin):
    list_display = ('id', 'computer_link', 'version_link', 'date')
    list_display_links = ('id',)
    list_select_related = ('computer', 'version')
    list_filter = ('date', 'version__platform', 'version')
    search_fields = add_computer_search_fields(['date'])
    fields = ('computer_link', 'version_link', 'date')
    readonly_fields = ('computer_link', 'version_link', 'date')
    exclude = ('computer',)
    actions = None

    computer_link = MigasFields.link(
        model=Migration, name='computer', order='computer__name'
    )
    version_link = MigasFields.link(
        model=Migration, name='version', order="version__name"
    )

    def has_add_permission(self, request):
        return False


@admin.register(Notification)
class NotificationAdmin(MigasAdmin):
    list_display = ('id', 'my_checked', 'date', 'my_notification')
    list_display_links = ('id',)
    list_filter = ('checked', 'date')
    ordering = ('-date',)
    search_fields = ('date', 'notification')
    readonly_fields = ('date', 'my_notification')
    exclude = ('notification',)
    actions = ['checked_ok']

    my_checked = MigasFields.boolean(model=Notification, name='checked')
    my_notification = MigasFields.text(model=Notification, name='notification')

    def checked_ok(self, request, queryset):
        for item in queryset:
            item.okay()

        messages.success(request, _('Checked %s') % _('Notifications'))

        return redirect(request.get_full_path())

    checked_ok.short_description = _("Checking is O.K.")

    def has_add_permission(self, request):
        return False


@admin.register(StatusLog)
class StatusLogAdmin(MigasAdmin):
    list_display = ('id', 'computer_link', 'status', 'created_at')
    list_display_links = ('id',)
    list_select_related = ('computer',)
    list_filter = ('created_at', ('status', ProductiveFilterSpec),)
    search_fields = add_computer_search_fields(['created_at'])
    readonly_fields = ('computer_link', 'status', 'created_at')
    exclude = ('computer',)
    actions = None

    computer_link = MigasFields.link(
        model=StatusLog, name='computer', order='computer__name'
    )

    def has_add_permission(self, request):
        return False


@admin.register(Update)
class UpdateAdmin(MigasAdmin):
    list_display = ('__str__', 'user_link', 'computer_link', 'version_link')
    list_display_links = ('__str__',)
    list_filter = ('date',)
    search_fields = add_computer_search_fields(['date', 'user__name'])
    readonly_fields = ('computer_link', 'user', 'version', 'date')
    exclude = ('computer',)
    actions = None

    computer_link = MigasFields.link(
        model=Update, name='computer', order='computer__name'
    )
    version_link = MigasFields.link(
        model=Update, name='version', order='version__name'
    )
    user_link = MigasFields.link(model=Update, name='user', order='user__name')

    def get_queryset(self, request):
        return super(UpdateAdmin, self).get_queryset(
            request
        ).select_related(
            'computer',
            'version',
            'user',
        )


@admin.register(User)
class UserAdmin(MigasAdmin):
    list_display = ('name_link', 'fullname')
    ordering = ('name',)
    search_fields = ('name', 'fullname')
    readonly_fields = ('name', 'fullname')

    name_link = MigasFields.link(model=User, name="name")

    def has_add_permission(self, request):
        return False


@admin.register(HwNode)
class HwNodeAdmin(MigasAdmin):  # TODO to hardware.py
    list_display = ('name_link',)

    name_link = MigasFields.link(model=HwNode, name='name')
