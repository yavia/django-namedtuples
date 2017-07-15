import pytest

from test_models.models import Point


@pytest.mark.django_db
def test_db():
    Point(x=1, y=2).save()
    assert Point.objects.get(x=1).y == 2
