from django.db import models
from django.contrib.auth.models import User


class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted=False)

class Task(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=25, choices=[
        ("new", "New"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
    ], default='new')
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted = models.BooleanField(default=False)
    category = models.ForeignKey("Category", on_delete=models.SET_NULL, null=True, blank=True)
    priority = models.ForeignKey("Priority", on_delete=models.SET_NULL, null=True, blank=True)

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    def __str__(self):
        return self.title

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted = models.BooleanField(default=False)

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    class Meta:
        unique_together = ("created_at", "name")

    def __str__(self):
        return self.name

class Priority(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted = models.BooleanField(default=False)

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    class Meta:
        unique_together = ("created_at", "name")

    def __str__(self):
        return self.name
