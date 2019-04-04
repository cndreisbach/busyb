import json

from django.contrib.auth.models import AnonymousUser
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View

from core.models import Task, User


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


@method_decorator(csrf_exempt, name='dispatch')
class TaskList(View):

    def get(self, request):
        check_user(request)
        if not request.user.is_authenticated:
            return JsonResponse({
                "status": "error",
                "message": "unauthorized",
            },
                                status=401)

        tasks = request.user.tasks.all()
        tasks_data = [task.to_dict() for task in tasks]
        return JsonResponse({"status": "ok", "data": tasks_data})

    def post(self, request):
        check_user(request)
        if not request.user.is_authenticated:
            return JsonResponse({
                "status": "error",
                "message": "unauthorized",
            },
                                status=401)

        task_data = json.loads(request.body)

        if task_data.get('description'):
            task = Task(
                owner=request.user, description=task_data['description'])
            task.save()
            return JsonResponse({
                "status": "ok",
                "data": task.to_dict()
            },
                                status=201)

        return JsonResponse({
            "status": "error",
            "errors": {
                "description": "cannot be blank"
            }
        },
                            status=400)


def task_detail(request, pk):
    check_user(request)
    if not request.user.is_authenticated:
        return JsonResponse({
            "status": "error",
            "message": "unauthorized",
        },
                            status=401)

    task = request.user.tasks.get(pk=pk)
    return JsonResponse({"status": "ok", "data": task.to_dict()})
