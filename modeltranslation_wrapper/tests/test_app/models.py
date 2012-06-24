from django.db import models

# Import manager from other file for testing forpose: this module is being reloaded
from manager import CustomManager


class News(models.Model):
    title = models.CharField(max_length=50)
    visits = models.SmallIntegerField(blank=True, null=True)


class Other(models.Model):
    name = models.CharField(max_length=50)

    objects = CustomManager()
