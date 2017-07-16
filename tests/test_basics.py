import uuid

import pytest

from django_namedtuples.queryset import namedtuples, ModelInterface
from test_models.models import Point, Car


@pytest.mark.django_db
def test_db():
    Point(x=1, y=2).save()
    assert Point.objects.get(x=1).y == 2


@pytest.mark.django_db
def test_namedtuplequeryset():
    car_id = 3
    car_color = u'green'
    Car(id=car_id, color=car_color).save()

    queryset = Car.objects.all()

    nt_queryset = namedtuples(
        queryset, 'id', 'color'
    )

    assert len(nt_queryset) == 1
    [car] = nt_queryset

    assert car == nt_queryset.get(id=car_id)
    assert car.id == car_id
    assert car.color == car_color
    assert repr(car) == 'CarTuple(id={!r}, color={!r})'.format(
        car_id, car_color
    )

    # test pk
    car2 = namedtuples(queryset, 'pk', 'id').get(id=car_id)
    assert car2.pk == car2.id == car_id

    randstring = uuid.uuid4()
    [car3] = namedtuples(queryset, computational={
        'str_id': lambda values: str(values[0]),
        'uuid': lambda values: randstring,
    })

    assert car3.str_id == str(car_id)
    assert car3.uuid == randstring


@pytest.mark.django_db
def test_namedtuple_computational_names_conflict():
    Car(color='red').save()

    with pytest.raises(ValueError) as e_info:
        namedtuples(
            Car.objects.all(), 'id', computational={'id': lambda row: row[0]}
        )
    assert isinstance(e_info.value, ValueError)
    assert str(e_info.value).startswith('Computational fields conflict')


@pytest.mark.django_db
def test_namedtuple_modelinterface():
    Car(color='red', year=1980).save()

    class CarInterface(ModelInterface):
        _fields = ('color', 'year', )

        def __str__(self):
            return u'{}:{}'.format(self.year, self.color)

    [car] = namedtuples(
        Car.objects.all(),
        'id', 'color',  # do not specify the year
        interface=CarInterface,
    )
    assert car.color == 'red'
    assert car.year == 1980
    assert str(car) == '1980:red'
    assert car.__class__.__name__ == 'CarTuple'


@pytest.mark.django_db
def test_modelinterface_uses_computational_fields():
    Car(color='yellow', year='2000').save()

    class CarInterface(ModelInterface):
        _fields = ('color', 'wheel_count')

        def is_yellow(self):
            return self.color == 'yellow'

        def has_four_wheels(self):
            return self.wheel_count == 4

    [car] = namedtuples(
        Car.objects.all(),
        'id',
        computational={'wheel_count': lambda values: 4},
        interface=CarInterface,
    )
    assert car.is_yellow()

    assert car.wheel_count == 4
    assert car.has_four_wheels()

