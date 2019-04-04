from django.urls import path, register_converter
from api import views
from core.hashids import HashidConverter

register_converter(HashidConverter, 'hashid')

urlpatterns = [
    path('tasks/', views.TaskList.as_view()),
    path('tasks/<hashid:hashid>/', views.TaskDetail.as_view()),
]
