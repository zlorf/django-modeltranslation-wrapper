from django.db import models


class CustomManager(models.Manager):
    def get_query_set(self):
        return super(CustomManager, self).get_query_set().filter(name__contains='a')

    def foo(self):
        return 'bar'
