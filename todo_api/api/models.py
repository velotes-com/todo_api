from queue import PriorityQueue

from django.db import models

# Create your models here.
class Task(models.Model):
    create_by = models.ForeignKey(User, on_delete=models.CASCADE),
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=25, choices=[
        ("new", "New"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
    ], default='new')
    completed = models.BooleanField(default=False)
    create_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted = models.BooleanField(default=False)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    priority = models.ForeignKey(Priority, on_delete=models.SET_NULL, null=True, blank=True)

class Category(models.Model):
    pass

class Primary(models.Model):
    pass