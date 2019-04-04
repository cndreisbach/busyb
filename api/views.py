import json

from django.contrib.auth.models import AnonymousUser
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View
from django.shortcuts import get_object_or_404

from core.models import User
from core.views import get_task_or_404
from api.forms import TaskForm


def check_user(request):
    if not request.user.is_authenticated:
        request.user = get_user_from_token(request)


def get_user_from_token(request):
    authorization_header = request.META['HTTP_AUTHORIZATION']
    if authorization_header.startswith("Token"):
        token = authorization_header[6:]
        try:
            user = User.objects.get(api_token=token)
            return user
        except User.DoesNotExist:
            return AnonymousUser()
    return AnonymousUser()


def parse_data(request):
    if request.body:
        request.data = json.loads(request.body)


class APIView(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        check_user(request)
        try:
            parse_data(request)
        except json.JSONDecodeError:
            return JsonResponse({
                "status": "error",
                "message": "bad request"
            },
                                status=400)
        if not request.user.is_authenticated:
            return JsonResponse({
                "status": "error",
                "message": "unauthorized",
            },
                                status=401)
        return super().dispatch(request, *args, **kwargs)


class TaskList(APIView):

    def get(self, request):
        tasks = request.user.tasks.all()
        tasks_data = [task.to_dict() for task in tasks]
        return JsonResponse({"status": "ok", "data": tasks_data})

    def post(self, request):
        form = TaskForm(data=request.data)

        if form.is_valid():
            task = form.save(commit=False)
            task.owner = request.user
            task.save()
            return JsonResponse({
                "status": "ok",
                "data": task.to_dict()
            },
                                status=201)

        return JsonResponse({
            "status": "error",
            "errors": form.errors.get_json_data()
        },
                            status=400)


class TaskDetail(APIView):

    def get(self, request, hashid):
        task = get_task_or_404(request, hashid)
        return JsonResponse({"status": "ok", "data": task.to_dict()})

    def put(self, request, hashid):
        return self.patch(request, hashid)

    def patch(self, request, hashid):
        task = get_task_or_404(request, hashid)
        if request.data.get('description'):
            task.description = request.data['description']
            task.save()

        return JsonResponse({"status": "ok", "data": task.to_dict()})

    def delete(self, request, hashid):
        task = get_task_or_404(request, hashid)
        task.delete()
        return JsonResponse({"status": "ok", "data": {"deleted": True}})
