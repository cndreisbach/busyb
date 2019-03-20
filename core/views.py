from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render, resolve_url
from django.views.decorators.http import require_http_methods
from django.http import Http404
from django.contrib import messages
from core.models import Tag
from core.forms import NewTaskForm, EditTaskForm, NoteForm
from datetime import date


def index(request):
    if request.user.is_authenticated:
        return redirect('task_list')

    return render(request, "core/index_logged_out.html")


@login_required
def task_list(request, group=None, tag=None):
    tasks = request.user.tasks

    header_text = 'Current tasks'

    if group == 'complete':
        tasks = tasks.complete()
        header_text = 'Completed tasks'
    elif group == 'future':
        tasks = tasks.future()
        header_text = 'Future tasks'
    else:
        tasks = tasks.current()

    tag = request.GET.get('tag')
    if tag:
        tasks = tasks.filter(tags__text__iexact=tag)
        header_text += f' tagged #{tag}'

    return render(
        request, "core/task_list.html", {
            "header_text": header_text,
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

    # If the form is submitted
    if request.method == 'POST':
        form = EditTaskForm(instance=task, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('task_list')
    else:
        form = EditTaskForm(instance=task)

    note_form = NoteForm()

    return render(
        request, "core/edit_task.html", {
            "form": form,
            "note_form": note_form,
            "task": task,
            "notes": task.notes.order_by('created_at')
        })


@require_http_methods(['POST'])
@login_required
def new_note(request, task_id):
    task = request.user.tasks.with_hashid(task_id)
    if task is None:
        raise Http404('No task matches the given query.')

    form = NoteForm(request.POST)

    if form.is_valid():
        note = form.save(commit=False)
        note.task = task
        note.save()
    else:
        messages.error(request, 'We had a problem saving your note.')

    redirect_url = resolve_url(to='edit_task', task_id=task.hashid)

    return redirect(to=f"{redirect_url}#note-{note.pk}")


@require_http_methods(['POST'])
@login_required
def new_task(request):
    form = NewTaskForm(request.POST)
    if form.is_valid():
        form.save(owner=request.user)
    return redirect('task_list')


@require_http_methods(['POST'])
@login_required
def mark_task_complete(request, task_id):
    task = request.user.tasks.with_hashid(task_id)
    if task is None:
        raise Http404('No task matches the given query.')
    task.mark_complete()
    return redirect('task_list')


@require_http_methods(['POST'])
@login_required
def mark_task_current(request, task_id):
    task = request.user.tasks.with_hashid(task_id)
    if task is None:
        raise Http404('No task matches the given query.')
    task.mark_current()
    return redirect('task_list_future')
