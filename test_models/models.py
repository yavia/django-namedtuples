from django.db.models import Model, IntegerField


class Point(Model):
    x = IntegerField(null=False)
    y = IntegerField(null=True)

    class Meta():
        unique_together = ('x', )
