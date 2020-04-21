# -*- coding: utf-8 -*-
from __future__ import absolute_import

from enum import Enum
from collections import namedtuple, OrderedDict
from itertools import chain

import django


DJANGO_VERSION_WITH_NEW_QUERYSET_STYLE = (1, 9)

if django.VERSION < DJANGO_VERSION_WITH_NEW_QUERYSET_STYLE:
    from django.db.models.query import ValuesQuerySet
else:
    from django.db.models.query import BaseIterable


class ModelInterface(object):
    _fields = ()


class UnderscoreStrategy(Enum):
    # NATIVE strategy forbids fields starting with an underscore, just like the namedtuple constructor
    # https://docs.python.org/2/library/collections.html#collections.namedtuple
    NATIVE = 0
    # LSTRIP strategy strips leading underscores from field names
    LSTRIP = 1


class BaseMaker(object):
    def __init__(self, base_queryset, computational, interface, underscore_strategy, fields):
        self.base_queryset = base_queryset
        self.computational = computational
        self.interface = interface
        self.underscore_strategy = underscore_strategy
        self.fields = fields

    def make_queryset(self):
        raise NotImplemented

    def get_names(self, queryset):
        raise NotImplemented

    def iterator(self, queryset, iterator_params):
        names = self.get_names(queryset)

        if self.underscore_strategy is UnderscoreStrategy.LSTRIP:
            names = [n.lstrip('_') for n in names]

        tuple_name = '{}Tuple'.format(queryset.model.__name__)
        tuple_cls = namedtuple(tuple_name, names)

        if self.interface:
            tuple_cls = type(
                tuple_name, (tuple_cls, self.interface,), {'_slots': ()},
            )

        if self.computational:
            computational_values = self.computational.values()
            instance = lambda values: tuple_cls._make(
                values + tuple(
                    func(values) for func in computational_values
                )
            )
        else:
            instance = tuple_cls._make

        # NOTE: we don't reorder the fields here, so they might go
        #       not in the order as in .namedtuples args if extra
        #       or aggregates are used.
        compiler = queryset.query.get_compiler(queryset.db)
        return (
            instance(values)
            for values in compiler.results_iter(**iterator_params)
        )


class ValuesQuerySetMaker(BaseMaker):
    def get_names(self, queryset):
        # Purge any extra columns that haven't been explicitly asked for
        return tuple(chain(
            queryset.query.extra_select.keys(),
            queryset.field_names,
            queryset.query.aggregate_select.keys(),
            self.computational.keys(),
        ))

    def make_queryset(self):
        maker = self

        class _NamedTuplesQuerySet(ValuesQuerySet):
            def _clone(self, klass=None, setup=False, **kwargs):
                return super(_NamedTuplesQuerySet, self)._clone(
                    klass, setup, **kwargs
                )

            def iterator(self):
                return maker.iterator(self, {})

        return maker.base_queryset._clone(
            klass=_NamedTuplesQuerySet, setup=True, _fields=maker.fields,
        )


class IterableQuerySetMaker(BaseMaker):
    def get_names(self, queryset):
        # Purge any extra columns that haven't been explicitly asked for
        return tuple(chain(
            queryset.query.extra_select.keys(),
            queryset.query.values_select,
            queryset.query.annotation_select.keys(),
            self.computational.keys(),
        ))

    def make_queryset(self):
        maker = self

        class NamedTupleIterable(BaseIterable):
            def __iter__(self):
                iterator_params = {}
                if hasattr(self, 'chunked_fetch'):
                    iterator_params = {'chunked_fetch': self.chunked_fetch}
                return maker.iterator(self.queryset, iterator_params)

        clone = self.base_queryset._values(*self.fields)
        clone._iterable_class = NamedTupleIterable
        return clone


def namedtuples(self, *fields, **kwargs):
    computational = OrderedDict(kwargs.pop('computational', {}))

    underscore_strategy = kwargs.pop('underscore_strategy', UnderscoreStrategy.LSTRIP)

    conflict_fields = set(computational) & set(fields)
    if conflict_fields:
        raise ValueError(
            'Computational fields conflict: {}'.format(conflict_fields)
        )

    interface = kwargs.pop('interface', None)
    if interface:
        if not issubclass(interface, ModelInterface):
            raise ValueError(
                'Param "interface" should be an instance of the ModelInterface'
            )

        # add the interface fields and keep the fields' order
        fields += tuple(
            set(interface._fields) - set(fields) - set(computational)
        )

    if django.VERSION < DJANGO_VERSION_WITH_NEW_QUERYSET_STYLE:
        maker = ValuesQuerySetMaker
    else:
        maker = IterableQuerySetMaker

    return maker(
        self, computational, interface, underscore_strategy, fields
    ).make_queryset()
