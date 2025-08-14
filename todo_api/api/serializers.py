from rest_framework import serializers
from django.utils import timezone
from django.contrib.auth.models import User
from .models import Task, Category, Priority


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password"]

    def create(self, validated_data):
        user = User(username=validated_data["username"], email=validated_data.get("email", ""))
        user.set_password(validated_data["password"])
        user.save()
        return user

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"
        read_only_fields = ['created_by',]

class PrioritySerializer(serializers.ModelSerializer):
    class Meta:
        model = Priority
        fields = "__all__"
        read_only_fields = ['created_by',]

class TaskSerializer(serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.filter(deleted=False), allow_null=True, required=False)
    priority = serializers.PrimaryKeyRelatedField(queryset=Category.objects.filter(deleted=False), allow_null=True, required=False)

    class Meta:
        model = Task
        fields = "__all__"
        read_only_fields = ['created_by',]

    def create(self, validated_data):
        if validated_data.get("completed") and not validated_data.get("completed_at"):
            validated_data["completed_at"] = timezone.now()
        return super().create(validated_data)

    def update(self, instance, validated_data):
        completed = validated_data.get("completed", instance.completed)
        if completed and not instance.completed_at and not validated_data.get("completed_at"):
            validated_data["completed_at"] = timezone.now()

        if not completed:
            validated_data["completed_at"] = None

        return super().update(instance, validated_data)
