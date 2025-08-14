from django.contrib.auth.models import User
from django.utils import timezone

from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from django_filters.rest_framework import DjangoFilterBackend

from .models import Task, Category, Priority
from .serializers import TaskSerializer, CategorySerializer, PrioritySerializer, UserSerializer


class IsOwnerOrAdmin(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.user and request.user.is_staff:
            return True
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_staff:
            return True
        owner = getattr(obj, "created_by", None)
        if owner is not None:
            return owner == request.user
        if isinstance(obj, User):
            return obj == request.user
        return False


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):

        if self.action in ["list", "retrieve", "update", "partial_update", "destroy", "reset_password"]:
            permission_classes = [permissions.IsAdminUser]
        elif self.action in ["create"]:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [p() for p in permission_classes]

    @action(detail=False, methods=["get", "patch", "delete"], url_path="me")
    def me(self, request):
        user = request.user

        if request.method.lower() == "get":
            return Response(self.get_serializer(user).data)

        elif request.method.lower() == "patch":
            ser = self.get_serializer(user, data=request.data, partial=True)
            ser.is_valid(raise_exception=True)
            ser.save()
            return Response(ser.data)

        elif request.method.lower() == "delete":
            user.is_active = False
            user.save(update_fields=["is_active"])
            Token.objects.filter(user=user).delete()
            return Response({"detail": "Account deactivated"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"])
    def change_password(self, request):
        user = request.user
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")
        if not old_password or not new_password:
            return Response({"detail": "old_password and new_password are required"}, status=status.HTTP_400_BAD_REQUEST)
        if not user.check_password(old_password):
            return Response({"detail": "Old password is incorrect"}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(new_password)
        user.save()
        Token.objects.filter(user=user).delete()
        return Response({"detail": "Password changed. Please login again."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"])
    def logout(self, request):
        Token.objects.filter(user=request.user).delete()
        return Response({"detail": "Logged out"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], permission_classes=[permissions.IsAdminUser])
    def reset_password(self, request):
        user_id = request.data.get("user_id")
        new_password = request.data.get("new_password")
        if not user_id or not new_password:
            return Response({"detail": "user_id and new_password are required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        user.set_password(new_password)
        user.save()
        Token.objects.filter(user=user).delete()
        return Response({"detail": "Password reset"}, status=status.HTTP_200_OK)


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ["status", "category", "priority"]
    ordering_fields = ["created_at", "status"]
    search_fields = ["title", "description", "status"]

    def get_queryset(self):

        if self.request.user.is_staff:
            return Task.objects.all()
        return Task.objects.filter(created_by=self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_destroy(self, instance):

        if self.request.user.is_staff:
            Task.all_objects.filter(pk=instance.pk).delete()
        else:
            instance.deleted = True
            instance.deleted_at = timezone.now()
            instance.save(update_fields=["deleted", "deleted_at"])


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ["created_at", "name"]
    search_fields = ["name", "description"]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Category.objects.all()
        return Category.objects.filter(created_by=self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_destroy(self, instance):
        if self.request.user.is_staff:
            Category.all_objects.filter(pk=instance.pk).delete()
        else:
            instance.deleted = True
            instance.deleted_at = timezone.now()
            instance.save(update_fields=["deleted", "deleted_at"])


class PriorityViewSet(viewsets.ModelViewSet):
    serializer_class = PrioritySerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ["created_at", "name"]
    search_fields = ["name"]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Priority.objects.all()
        return Priority.objects.filter(created_by=self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_destroy(self, instance):
        if self.request.user.is_staff:
            Priority.all_objects.filter(pk=instance.pk).delete()
        else:
            instance.deleted = True
            instance.deleted_at = timezone.now()
            instance.save(update_fields=["deleted", "deleted_at"]) 
