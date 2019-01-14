import json

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods
from core.forms import NewTaskForm


def index(request):
    if request.user.is_authenticated:
        return render(request, "core/index.html", {
            "tasks": request.user.tasks,
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


@login_required
def dashboard(request):
    user = request.user
    auth0user = user.social_auth.get(provider='auth0')
    userdata = {
        'user_id': auth0user.uid,
        'name': user.first_name,
        'picture': auth0user.extra_data['picture']
    }

    return render(request, 'core/dashboard.html', {
        'auth0User': auth0user,
        'userdata': json.dumps(userdata, indent=4)
    })
