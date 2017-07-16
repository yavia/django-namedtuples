from django.db.models import Model, IntegerField, CharField, ForeignKey


class Point(Model):
    x = IntegerField()
    y = IntegerField(null=True)

    class Meta():
        unique_together = ('x', )


class Car(Model):
    color = CharField(max_length=1000)
    year = IntegerField(null=True)
