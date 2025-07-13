from rest_framework import serializers
from django.contrib.auth.models import User
from apps.tasks.models import Task



class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model
    """
    task_count = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'task_count']
        read_only_fields = ['id']
    
    def get_task_count(self, obj):
        """Get total number of tasks for this user"""
        return obj.tasks.count()