from django.shortcuts import render
from core.models import Task, User
from django.http import JsonResponse


def get_user(request):
    authorization_header = request.META['HTTP_AUTHORIZATION']
    if authorization_header.startswith("Token"):
        token = authorization_header[6:]
        try:
            user = User.objects.get(api_token=token)
            return user
        except User.DoesNotExist:
            return None


# Create your views here.
def task_list(request):
    user = get_user(request)
    if not user:
        return JsonResponse({
            "status": "error",
            "message": "unauthorized",
        },
                            status=401)

    tasks = user.tasks.all()
    tasks_data = [task.to_dict() for task in tasks]
    return JsonResponse({"status": "ok", "data": tasks_data})


def task_detail(request, pk):
    user = get_user(request)
    if not user:
        return JsonResponse({
            "status": "error",
            "message": "unauthorized",
        },
                            status=401)

    task = user.tasks.get(pk=pk)
    return JsonResponse({"status": "ok", "data": task.to_dict()})
