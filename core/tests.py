import pytest
from datetime import date, timedelta
from core.models import Task, User


@pytest.mark.django_db
@pytest.fixture
def user():
    return User.objects.create_user('test', 'test@example.org')


@pytest.mark.django_db
def test_task_visibility(user):
    task_no_show_on = Task.objects.create(description='task0', owner=user)
    task_show_on_today = Task.objects.create(
        description='task1', show_on=date.today(), owner=user)
    task_show_on_tomorrow = Task.objects.create(
        description='task2',
        show_on=date.today() + timedelta(days=1),
        owner=user)

    visible_tasks = Task.objects.visible()
    assert task_no_show_on in visible_tasks
    assert task_show_on_today in visible_tasks
    assert task_show_on_tomorrow not in visible_tasks


@pytest.mark.django_db
def test_todos_for_user(user):
    other_user = User.objects.create_user('test2')

    task_no_show_on = Task.objects.create(description='task0', owner=user)
    task_show_on_today = Task.objects.create(
        description='task1', show_on=date.today(), owner=user)
    task_complete = Task.objects.create(description='complete', owner=user)
    task_complete.mark_complete()
    task_show_on_tomorrow = Task.objects.create(
        description='task2',
        show_on=date.today() + timedelta(days=1),
        owner=user)
    task_other_user = Task.objects.create(
        description='other_user_task', owner=other_user)

    todos = Task.objects.todos_for_user(user)
    assert task_no_show_on in todos
    assert task_show_on_today in todos
    assert task_show_on_tomorrow not in todos
    assert task_other_user not in todos
    assert task_complete not in todos
