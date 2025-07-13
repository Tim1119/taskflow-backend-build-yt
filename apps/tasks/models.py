from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator
import uuid





class PriorityChoices(models.TextChoices):
    LOW = 'Low', 'Low'
    MEDIUM = 'Medium', 'Medium'
    HIGH = 'High', 'High'

class Task(models.Model):
    pkid = models.BigAutoField(primary_key=True, editable=False)
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(max_length=250,validators=[MinLengthValidator(1)],help_text="Task title (max 250 charcaters)")
    description = models.TextField(blank=True,null=True,help_text="Optional task description")
    completed= models.BooleanField(default=False,help_text="Whether task is completed")
    priority = models.CharField(max_length=6,choices=PriorityChoices.choices,default=PriorityChoices.MEDIUM,help_text="Priority task level")
    due_date = models.DateTimeField(blank=True,null=True,help_text="Optional due date for the task")
    category = models.CharField(max_length=100,blank=True,null=True,help_text="Optional category/tag for the task")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="tasks")

    class Meta:
        ordering = ['-created_at']  # Newest tasks first
        indexes = [
            models.Index(fields=['user', 'completed']),
            models.Index(fields=['user', 'priority']),
            models.Index(fields=['due_date']),
        ]
    
    def __str__(self):
        return f"{self.title} ({'✓' if self.completed else '○'})"
    
    @property
    def is_overdue(self):
        """Check if task is overdue"""
        if self.due_date and not self.completed:
            from django.utils import timezone
            return self.due_date < timezone.now()
        return False



# Create your models here.
