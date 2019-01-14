from django.db import models

from django.contrib.auth.models import AbstractUser
from core.hashids import hashids


class User(AbstractUser):
    pass


class TaskQuerySet(models.QuerySet):

    def with_hashid(self, hashid):
        ids = hashids.decode(hashid)
        if len(ids) == 1:
            return self.get(pk=ids[0])
        return self.filter(pk__in=ids)


class Task(models.Model):

    class Meta:
        base_manager_name = 'objects'

    objects = TaskQuerySet.as_manager()
    description = models.CharField(max_length=512)
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='tasks')

    @property
    def hashid(self):
        return hashids.encode(self.pk)
