# -*- coding: utf-8 -*-
from __future__ import absolute_import

from enum import Enum
from collections import namedtuple, OrderedDict
from itertools import chain

from django.db.models.query import ValuesQuerySet


class ModelInterface(object):
    _fields = ()


class UnderscoreStrategy(Enum):
    # NATIVE strategy forbids fields starting with an underscore, just like the namedtuple constructor
    # https://docs.python.org/2/library/collections.html#collections.namedtuple
    NATIVE = 0
    # LSTRIP strategy strips leading underscores from field names
    LSTRIP = 1


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

    class NamedTuplesQuerySet(ValuesQuerySet):
        def _clone(self, klass=None, setup=False, **kwargs):
            return super(NamedTuplesQuerySet, self)._clone(
                klass, setup, **kwargs
            )

        def iterator(self):
            # Purge any extra columns that haven't been explicitly asked for
            names = tuple(chain(
                self.query.extra_select.keys(),
                self.field_names,
                self.query.aggregate_select.keys(),
                computational.keys(),
            ))
            if underscore_strategy is UnderscoreStrategy.LSTRIP:
                names = [n.lstrip('_') for n in names]

            tuple_name = '{}Tuple'.format(self.model.__name__)
            tuple_cls = namedtuple(tuple_name, names)

            if interface:
                tuple_cls = type(
                    tuple_name, (tuple_cls, interface,), {'_slots': ()},
                )

            if computational:
                computational_values = computational.values()
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
            return (
                instance(values)
                for values in self.query.get_compiler(self.db).results_iter()
            )

    return self._clone(
        klass=NamedTuplesQuerySet, setup=True, _fields=fields,
    )
