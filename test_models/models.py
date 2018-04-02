from django.db.models import Model, IntegerField, CharField


class Point(Model):
    x = IntegerField()
    y = IntegerField(null=True)

    class Meta():
        unique_together = ('x', )


class Car(Model):
    color = CharField(max_length=1000)
    year = IntegerField(null=True)


class City(Model):
    _geo_id = IntegerField()
    title = CharField(max_length=1000)
