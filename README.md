Django Namedtuples
- 

This library allows to select django models in form of [namedtuples](https://docs.python.org/2/library/collections.html#collections.namedtuple).

Namedtuples are immutable and memory efficient, although their field 
access is usually 2-3 times slower than for regular classes.

The main purpose of this library is to allow to cache django models 
in a safe and and memory efficient way.


Usage:
```python
from django_namedtuples import patch_django_queryset
from models import Car

patch_django_queryset()



car_tuple = Car.objects.all().namedtuples(
    'id', 'make', 'model', 'color'
)[0]

print car_tuple  # CarTuple(id=100, make='BMW', model='X6', color='black')
print car_tuple.id  # 100
print car_tuple[1]  # BMW
car_tuple.color = 'white'  # AttributeError: can't set attribute



second_car_tuple = Car.objects.all().namedtuples(
    'id', 'make', 'model', 'color',
    computational={
        'country': lambda row: 'Germany' if row[1] == 'BMW' else 'Unknown',
        'constant_attr': 100
    }
).get(id=200)

print second_car_tuple
# CarTuple(id=100, make='BMW', model='X6', color='white', country='Germany', constant_attr=100)
[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bhttps%3A%2F%2Fgithub.com%2Fyavia%2Fdjango-namedtuples.svg?type=shield)](https://app.fossa.io/projects/git%2Bhttps%3A%2F%2Fgithub.com%2Fyavia%2Fdjango-namedtuples?ref=badge_shield)


```


## License
[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bhttps%3A%2F%2Fgithub.com%2Fyavia%2Fdjango-namedtuples.svg?type=large)](https://app.fossa.io/projects/git%2Bhttps%3A%2F%2Fgithub.com%2Fyavia%2Fdjango-namedtuples?ref=badge_large)