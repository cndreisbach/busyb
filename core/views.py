from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import json


# Create your views here.
def index(req):
    if req.user.is_authenticated:
        return render(req, "core/index.html")

    return render(req, "core/index_logged_out.html")


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
