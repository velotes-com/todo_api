from rest_framework import viewsets, permissions, filters

from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone

from .models import Task, Category, Priority
from .serializers import TaskSerializer, CategorySerializer, PrioritySerializer, UserSerializer
from django.contrib.auth.models import User


class IsOwnerOrAdmin(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        owner = getattr(obj, "created_by", None)
        return owner == request.user

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]

class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ["created_at", "status"]
    search_fields = ["title", "description", "status"]

    def get_queryset(self):
        qs = Task.objects.filter(created_by=self.request.user, deleted=False)
        status_param = self.request.query_params.get('status')
        category_param = self.request.query_params.get('category')
        priority_param = self.request.query_params.get('priority')
        if status_param:
            qs = qs.filter(status=status_param)
        if category_param:
            qs = qs.filter(category__id=category_param)
        if priority_param:
            qs = qs.filter(priority__id=priority_param)
        return qs

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_destroy(self, instance):
        if self.request.user.is_staff:
            instance.delete()
        else:
            instance.deleted = True
            instance.deleted_at = timezone.now()
            instance.save()


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ["created_at", "name"]
    search_fields = ["name", "description"]

    def get_queryset(self):
        return Category.objects.filter(created_by=self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_destroy(self, instance):
        if self.request.user.is_staff:
            instance.delete()
        else:
            instance.deleted = True
            instance.deleted_at = timezone.now()
            instance.save()


class PriorityViewSet(viewsets.ModelViewSet):
    serializer_class = PrioritySerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ["created_at", "name"]
    search_fields = ["name"]

    def get_queryset(self):
        return Priority.objects.filter(created_by=self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_destroy(self, instance):
        if self.request.user.is_staff:
            instance.delete()
        else:
            instance.deleted = True
            instance.deleted_at = timezone.now()
            instance.save()
