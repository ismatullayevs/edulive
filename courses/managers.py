from django.db import models


class CouseManager(models.Manager):
    def get_queryset(self):
        return super(CouseManager, self).get_queryset().filter(active=True)
