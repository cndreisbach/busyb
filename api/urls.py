from django.urls import path
from api import views

urlpatterns = [
    path('tasks/', views.task_list),
    path('tasks/<int:pk>/', views.task_detail),
]
