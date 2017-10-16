# -*- coding: utf-8 -*-

from rest_framework import viewsets, filters, status
from rest_framework_filters import backends
from rest_framework.decorators import list_route
from rest_framework.response import Response

from migasfree.server.permissions import PublicPermission
from . import models, serializers
from .filters import ApplicationFilter, PackagesByProjectFilter, PolicyFilter


class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = models.Application.objects.all()
    serializer_class = serializers.ApplicationSerializer
    filter_class = ApplicationFilter
    filter_backends = (filters.OrderingFilter, backends.DjangoFilterBackend)
    permission_classes = (PublicPermission,)

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'update' \
                or self.action == 'partial_update':
            return serializers.ApplicationWriteSerializer

        return serializers.ApplicationSerializer

    @list_route(methods=['get'])
    def levels(self, request):
        return Response(
            dict(models.Application.LEVELS),
            status=status.HTTP_200_OK
        )

    @list_route(methods=['get'])
    def categories(self, request):
        return Response(
            dict(models.Application.CATEGORIES),
            status=status.HTTP_200_OK
        )


class PackagesByProjectViewSet(viewsets.ModelViewSet):
    queryset = models.PackagesByProject.objects.all()
    serializer_class = serializers.PackagesByProjectSerializer
    filter_class = PackagesByProjectFilter
    filter_backends = (filters.OrderingFilter, backends.DjangoFilterBackend)
    permission_classes = (PublicPermission,)

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'update' \
                or self.action == 'partial_update':
            return serializers.PackagesByProjectWriteSerializer

        return serializers.PackagesByProjectSerializer


class PolicyViewSet(viewsets.ModelViewSet):
    queryset = models.Policy.objects.all()
    serializer_class = serializers.PolicySerializer
    filter_class = PolicyFilter
    filter_backends = (filters.OrderingFilter, backends.DjangoFilterBackend)

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'update' \
                or self.action == 'partial_update':
            return serializers.PolicyWriteSerializer

        return serializers.PolicySerializer


class PolicyGroupViewSet(viewsets.ModelViewSet):
    queryset = models.PolicyGroup.objects.all()
    serializer_class = serializers.PolicyGroupSerializer
    filter_backends = (filters.OrderingFilter, backends.DjangoFilterBackend)

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'update' \
                or self.action == 'partial_update':
            return serializers.PolicyGroupWriteSerializer

        return serializers.PolicyGroupSerializer
