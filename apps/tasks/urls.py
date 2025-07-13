from django.urls import path
from .views import *



urlpatterns = [
    # Task CRUD operations
  
    path('tasks/', TaskListCreateView.as_view(), name='task-list-create'),
    path('tasks/<int:pk>/', TaskDetailView.as_view(), name='task-detail'),
    
    # Additional endpoints
    path('tasks/stats/', task_statistics, name='task-stats'),
    path('tasks/bulk-update/', bulk_update_tasks, name='bulk-update'),
]