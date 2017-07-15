from __future__ import absolute_import

from django.db.models.query import QuerySet

_patched = []


def patch_django_queryset():
    from .queryset import namedtuples

    try:
        _patched.append(QuerySet.namedtuples)
    except Exception:
        pass
    QuerySet.namedtuples = namedtuples


def unpatch_django_queryset():
    if _patched:
        QuerySet.namedtuples = _patched.pop()
