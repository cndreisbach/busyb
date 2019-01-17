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
        return self.filter(completed_at__isnull=False)

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
    created_at = models.DateTimeField(null=True, auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    due_on = models.DateField(null=True, blank=True)
    show_on = models.DateField(null=True, blank=True)

    @property
    def hashid(self):
        return hashids.encode(self.pk)

    def mark_complete(self, save=True):
        """
        Mark task as completed at current time.
        Saves completion to DB until `save` is set to False.
        """
        self.completed_at = timezone.now()
        if save:
            self.save()
        return self
