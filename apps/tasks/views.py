from django.shortcuts import render
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from django.db.models import Q
from .models import Task
from .serializers import TaskSerializer, TaskCreateSerializer
import logging


logger = logging.getLogger(__name__)

# Create your views here.

class TaskListCreateView(generics.ListCreateAPIView):
    """
    GET: List all tasks for the authenticated user
    POST: Create a new task for the authenticated user
    """

    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter tasks to only show user's own tasks"""
        user = self.request.user
        queryset = Task.objects.filter(user=user)

        completed = self.request.query_params.get('completed',None)
        priority= self.request.query_params.get('priority',None)
        search = self.request.query_params.get('search',None)

        if completed is not None:
            queryset = queryset.filter(completed = completed.lower()=='true')
        if priority is not None:
            queryset = queryset.filter(priority = priority.upper())
        if search is not None:
            queryset = queryset.filter(Q(title__icontains=search)|Q(description___icontains=search))
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        logger.info(f"Task created by user {self.request.user.username}")


class TaskDetailView(generics.RetrieveDestroyAPIView):
    """
    GET: Retrieve a specific task
    PUT/PATCH: Update a specific task
    DELETE: Delete a specific task
    """

    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def task_statistics(request):
    """
    Get task statistics for the authenticated user
    """
    user = request.user
    tasks = Task.objects.filter(user=user)

    total_tasks = tasks.count()
    completed_tasks = tasks.filter(completed=True)
    pending_tasks =  total_task - completed_task

    high_priority = tasks.filter(priority="HIGH").count()
    medium_priority = tasks.filter(priority="MEDIUM").count()
    low_priority = tasks.filter(priority="LOW").count()

    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

    stats = {
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'pending_tasks': pending_tasks,
        'completion_rate': round(completion_rate, 2),
        'priority_breakdown': {
            'high': high_priority,
            'medium': medium_priority,
            'low': low_priority,
        }
    }
    
    return Response(stats)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bulk_update_tasks(request):
    """
    Bulk update multiple tasks (e.g., mark multiple as completed)
    """
    task_ids = request.data.get('task_ids', [])
    action = request.data.get('action', '')
    
    if not task_ids or not action:
        return Response(
            {'error': 'task_ids and action are required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get user's tasks only
    tasks = Task.objects.filter(
        id__in=task_ids, 
        user=request.user
    )
    
    if action == 'complete':
        updated = tasks.update(completed=True)
    elif action == 'incomplete':
        updated = tasks.update(completed=False)
    elif action == 'delete':
        updated = tasks.count()
        tasks.delete()
    else:
        return Response(
            {'error': 'Invalid action. Use: complete, incomplete, or delete'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    return Response({
        'message': f'{updated} tasks {action}d successfully',
        'updated_count': updated
    })
