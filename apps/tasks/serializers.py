from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Task

class TaskSerializer(serializers.ModelSerializer):
    """
    Serializer for Task model - converts between Python objects and JSON
    """
    user = serializers.StringRelatedField(read_only=True)  # Show username instead of ID
    is_overdue = serializers.ReadOnlyField()  # Include our custom property
    
    class Meta:
        model = Task
        fields = [
            'id', 
            'title', 
            'description', 
            'completed', 
            'priority', 
            'due_date', 
            'category',
            'created_at', 
            'updated_at', 
            'user',
            'is_overdue'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'user']
    
    def validate_title(self, value):
        """Custom validation for title field"""
        if len(value.strip()) < 1:
            raise serializers.ValidationError("Title cannot be empty")
        return value.strip()
    
    def validate_priority(self, value):
        """Ensure priority is uppercase"""
        return value.upper()

class TaskCreateSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for task creation
    """
    class Meta:
        model = Task
        fields = ['title', 'description', 'priority', 'due_date', 'category']
    
    def validate_title(self, value):
        if not value or len(value.strip()) < 1:
            raise serializers.ValidationError("Title is required")
        return value.strip()
