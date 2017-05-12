# -*- coding: utf-8 -*-
from __future__ import absolute_import

from itertools import imap
from collections import namedtuple, OrderedDict

from django.db.models.query import ValuesQuerySet


class ModelInterface(object):
    _fields = ()


class NamedTuplesQuerySet(ValuesQuerySet):
    def _clone(self, klass=None, setup=False, **kwargs):
        c = super(NamedTuplesQuerySet, self)._clone(klass, setup, **kwargs)
        return c

    def iterator(self):
        # Purge any extra columns that haven't been explicitly asked for
        extra_names = self.query.extra_select.keys()
        field_names = self.field_names
        aggregate_names = self.query.aggregate_select.keys()
        computational = self._computational_namedtuple_fields
        names = extra_names + field_names + aggregate_names + computational.keys()

        tuple_name = '%sTuple' % self.model.__name__
        tuple_cls = namedtuple(tuple_name, names)

        iface = self._namedtuple_interface
        if iface:
            tuple_cls = type(tuple_name, (tuple_cls, iface,), {'_slots': ()})

        if computational:
            computational_values = computational.values()
            def make_tuple_instance(values):
                return tuple_cls._make(
                    values +
                    tuple([_c(values) for _c in computational_values])
                )
        else:
            make_tuple_instance = tuple_cls._make

        # NOTE: we are not reordering fields here,
        #       so they can go not in that order as in .namedtuples args
        #       if extra or aggregates are used.
        results_iter = self.query.get_compiler(self.db).results_iter()
        return imap(make_tuple_instance, results_iter)


def namedtuples(self, *fields, **kwargs):
    computational = kwargs.pop('computational', {})
    if not isinstance(computational, dict):
        raise ValueError

    computational = OrderedDict(computational)
    conflict_fields = set(computational) & set(fields)
    if conflict_fields:
        raise ValueError(
            'Computational fields conflicts: {}'.format(conflict_fields)
        )

    interface = kwargs.pop('interface', None)
    if interface:
        if not issubclass(interface, ModelInterface):
            raise ValueError(
                'Param "interface" should be an instance of the ModelInterface'
            )
        # Сохраняя порядок полей, нужно добавиь в зарос недостающие поля
        # интерфейса, если они не в списке вычисляемых
        fields += tuple(
            set(interface._fields) - set(fields) - set(computational)
        )

    class _NamedTuplesQuerySet(NamedTuplesQuerySet):
        _namedtuple_interface = interface
        _computational_namedtuple_fields=computational

    c = self._clone(
        klass=_NamedTuplesQuerySet, setup=True, _fields=fields,
    )
    return c
