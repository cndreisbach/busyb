from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods
from django.http import Http404

from core.forms import NewTaskForm, EditTaskForm
from datetime import date


def index(request):
    if request.user.is_authenticated:
        return task_list(request)

    return render(request, "core/index_logged_out.html")


@login_required
def task_list(request, group=None):
    tasks = request.user.tasks

    if group == 'complete':
        tasks = tasks.complete()
    elif group == 'future':
        tasks = tasks.future()
    else:
        tasks = tasks.current()

    return render(request, "core/task_list.html", {
        "today": date.today(),
        "tasks": tasks,
        "form": NewTaskForm()
    })


@require_http_methods(['GET', 'POST'])
@login_required
def edit_task(request, task_id):
    task = request.user.tasks.with_hashid(task_id)
    if task is None:
        raise Http404('No task matches the given query.')
    form = EditTaskForm(instance=task)
    return render(request, "core/edit_task.html", {"form": form})


@require_http_methods(['POST'])
@login_required
def new_task(request):
    form = NewTaskForm(request.POST)
    if form.is_valid():
        form.save(owner=request.user)
    return redirect('index')


@require_http_methods(['POST'])
@login_required
def mark_task_complete(request, task_id):
    task = request.user.tasks.with_hashid(task_id)
    if task is None:
        raise Http404('No task matches the given query.')
    task.mark_complete()
    return redirect('index')


@require_http_methods(['POST'])
@login_required
def mark_task_current(request, task_id):
    task = request.user.tasks.with_hashid(task_id)
    if task is None:
        raise Http404('No task matches the given query.')
    task.mark_current()
    return redirect('task_list_future')
