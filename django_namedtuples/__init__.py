from __future__ import absolute_import


def patch_django_queryset():
    from django.db.models.query import QuerySet
    from .queryset import namedtuples
    QuerySet.namedtuples = namedtuples
