import json

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods
from core.forms import NewTaskForm


def index(request):
    if request.user.is_authenticated:
        return render(
            request, "core/index.html", {
                "tasks": request.user.tasks.visible().incomplete(),
                "form": NewTaskForm()
            })

    return render(request, "core/index_logged_out.html")


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
    task.mark_complete()
    return redirect('index')
