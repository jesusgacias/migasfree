# -*- coding: utf-8 -*-

from django.conf import settings
from django.db.models import Q

from dal import autocomplete

from ..models import Computer, Attribute, Device, UserProfile


class AutocompleteModelBase(autocomplete.Select2QuerySetView):
    """
    Adaptation from
    https://github.com/yourlabs/django-autocomplete-light/blob/2.3.3/autocomplete_light/autocomplete/model.py
    """

    def _construct_search(self, field_name):
        """
        Using a field name optionally prefixed by `^`, `=`, `@`, return a
        case-insensitive filter condition name usable as a queryset `filter()`
        keyword argument.
        """
        if field_name.startswith('^'):
            return '{}__istartswith'.format(field_name[1:])
        elif field_name.startswith('='):
            return '{}__iexact'.format(field_name[1:])
        elif field_name.startswith('@'):
            return '{}__search'.format(field_name[1:])
        else:
            return '{}__icontains'.format(field_name)

    def choices_for_request_conditions(self, q, search_fields):
        """
        Return a `Q` object usable by `filter()` based on a list of fields to
        search in `search_fields` for string `q`.
        """
        conditions = Q()

        for search_field in search_fields:
            conditions |= Q(**{self._construct_search(search_field): q})

        return conditions


class ComputerAutocomplete(AutocompleteModelBase):
    search_fields = settings.MIGASFREE_COMPUTER_SEARCH_FIELDS

    def get_queryset(self):
        if not self.request.user.is_authenticated():
            return Computer.objects.none()

        qs = Computer.objects.all()

        if self.q:
            conditions = self.choices_for_request_conditions(
                self.q, self.search_fields
            )
            qs = qs.filter(conditions)

        return qs

    def get_result_label(self, result):
        return result.__str__()


class AttributeAutocomplete(AutocompleteModelBase):
    search_fields = ['^property_att__prefix', 'value']

    def get_queryset(self):
        if not self.request.user.is_authenticated():
            return Attribute.objects.none()

        qs = Attribute.objects.all()

        if self.q:
            conditions = self.choices_for_request_conditions(
                self.q, self.search_fields
            )
            qs = qs.filter(conditions)

        return qs


class DeviceAutocomplete(AutocompleteModelBase):
    search_fields = ['name', 'data']

    def get_queryset(self):
        if not self.request.user.is_authenticated():
            return Device.objects.none()

        qs = Device.objects.all()

        if self.q:
            conditions = self.choices_for_request_conditions(
                self.q, self.search_fields
            )
            qs = qs.filter(conditions)

        return qs

    def get_result_label(self, result):
        return '{} {} @ {}'.format(
            result.__str__(),
            result.model.name,
            result.location()
        )


class UserProfileAutocomplete(AutocompleteModelBase):
    search_fields = ['username', 'first_name', 'last_name']

    def get_queryset(self):
        if not self.request.user.is_authenticated():
            return UserProfile.objects.none()

        qs = UserProfile.objects.all()

        if self.q:
            conditions = self.choices_for_request_conditions(
                self.q, self.search_fields
            )
            qs = qs.filter(conditions)

        return qs.order_by('username')
