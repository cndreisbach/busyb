from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, F, Max
from django.http import Http404, JsonResponse
from django.shortcuts import redirect, render, resolve_url
from django.views.decorators.http import require_http_methods
from django.views.generic import ListView, View

from core.forms import EditTaskForm, NewTaskForm, NoteForm
from core.models import Task
from django.core.serializers import serialize


def index(request):
    if request.user.is_authenticated:
        return redirect('task_list')

    return render(request, "core/index_logged_out.html")


class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    context_object_name = 'tasks'
    template_name = 'core/task_list.html'

    def get_queryset(self):
        self.group = self.kwargs.get('group')
        self.tag = self.request.GET.get('tag')
        self.sort = self.request.GET.get('sort')

        tasks = self.request.user.tasks
        if self.group == 'complete':
            tasks = tasks.complete()
        elif self.group == 'future':
            tasks = tasks.future()
        else:
            tasks = tasks.current()

        if self.tag:
            tasks = tasks.filter(tags__text__iexact=self.tag)

        tasks = tasks.annotate(
            note_count=Count('notes'),
            last_note_created_at=Max('notes__created_at'))

        if self.sort in [
                'created_at', 'due_on', 'last_note_created_at', 'note_count'
        ]:
            tasks = tasks.order_by(
                F(self.sort).desc(nulls_last=True), 'description')

        return tasks

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        header_text = 'Current tasks'

        if self.group == 'complete':
            header_text = 'Completed tasks'
        elif self.group == 'future':
            header_text = 'Future tasks'

        if self.tag:
            header_text += f' tagged #{self.tag}'

        context["today"] = date.today()
        context["form"] = NewTaskForm()
        context["header_text"] = header_text
        context["sort"] = self.sort
        return context


class EditTaskView(LoginRequiredMixin, View):

    def dispatch(self, request, *args, **kwargs):
        self.task = request.user.tasks.with_hashid(kwargs['task_id'])
        self.note_form = NoteForm()
        if self.task is None:
            raise Http404('No task matches the given query.')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, task_id):
        form = EditTaskForm(instance=self.task)

        return render(
            request, "core/edit_task.html", {
                "form": form,
                "note_form": self.note_form,
                "task": self.task,
                "notes": self.task.notes.order_by('created_at')
            })

    def post(self, request, task_id):
        form = EditTaskForm(instance=self.task, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('task_list')

        return render(
            request, "core/edit_task.html", {
                "form": form,
                "note_form": self.note_form,
                "task": self.task,
                "notes": self.task.notes.order_by('created_at')
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

    if request.is_ajax():
        return JsonResponse({"complete": True})

    return redirect('task_list')


@require_http_methods(['POST'])
@login_required
def mark_task_current(request, task_id):
    task = request.user.tasks.with_hashid(task_id)
    if task is None:
        raise Http404('No task matches the given query.')
    task.mark_current()

    if request.is_ajax():
        return JsonResponse(serialize('json', task))

    return redirect('task_list_future')
