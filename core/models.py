from django.db import models
from django.db.models import Q

from django.contrib.auth.models import AbstractUser
from core.hashids import hashids
from datetime import date
from django.utils import timezone


class User(AbstractUser):
    pass


class TaskQuerySet(models.QuerySet):

    def with_hashid(self, hashid):
        ids = hashids.decode(hashid)
        # TODO add check -- if len is 0, hashid is invalid, should raise exception
        if len(ids) == 1:
            return self.get(pk=ids[0])
        return self.filter(pk__in=ids)

    def incomplete(self):
        return self.filter(completed_at__isnull=True)

    def complete(self):
        return self.filter(completed_at__isnull=False).order_by('completed_at')

    def current(self):
        return self.incomplete().filter(
            Q(show_on__isnull=True) | Q(show_on__lte=date.today()))

    def future(self):
        return self.incomplete().filter(
            show_on__isnull=False, show_on__gt=date.today())


class Task(models.Model):

    class Meta:
        base_manager_name = 'objects'

    objects = TaskQuerySet.as_manager()
    description = models.CharField(max_length=512)
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='tasks')
    created_at = models.DateTimeField(null=True, auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    due_on = models.DateField(null=True, blank=True)
    show_on = models.DateField(null=True, blank=True)

    @property
    def hashid(self):
        return hashids.encode(self.pk)

    def is_complete(self):
        return self.completed_at is not None

    def is_current(self):
        return not self.is_complete() and (self.show_on is None or
                                           self.show_on <= date.today())

    def is_future(self):
        return not self.is_complete() and (self.show_on is not None and
                                           self.show_on > date.today())

    def mark_complete(self, save=True):
        """
        Mark task as completed at current time.
        Saves completion to DB until `save` is set to False.
        """
        self.completed_at = timezone.now()
        if save:
            self.save()
        return self

    def mark_current(self, save=True):
        """
        Mark task as current by removing show_on.
        Saves completion to DB until `save` is set to False.
        """
        self.show_on = None
        if save:
            self.save()
        return self
