from django.db import models
from django.db.models import Q

from django.contrib.auth.models import AbstractUser
from core.hashids import hashids
from datetime import date


class User(AbstractUser):
    pass


class TaskQuerySet(models.QuerySet):

    def with_hashid(self, hashid):
        ids = hashids.decode(hashid)
        if len(ids) == 1:
            return self.get(pk=ids[0])
        return self.filter(pk__in=ids)

    def incomplete(self):
        return self.filter(complete=False)

    def complete(self):
        return self.filter(complete=True)

    def visible(self):
        return self.filter(
            Q(show_on__isnull=True) | Q(show_on__lte=date.today()))

    def todos_for_user(self, user):
        """
        This is the standard set a user should see: for them, visible, incomplete.
        """
        return self.filter(owner=user).incomplete().visible()


class Task(models.Model):

    class Meta:
        base_manager_name = 'objects'

    objects = TaskQuerySet.as_manager()
    description = models.CharField(max_length=512)
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='tasks')
    complete = models.BooleanField(default=False)
    due_on = models.DateField(null=True, blank=True)
    show_on = models.DateField(null=True, blank=True)

    @property
    def hashid(self):
        return hashids.encode(self.pk)
