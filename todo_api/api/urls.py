from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TaskViewSet, CategoryViewSet, PriorityViewSet, UserViewSet


router = DefaultRouter()
router.register(r'task', TaskViewSet, basename='task')
router.register(r'categories', CategoryViewSet, basename="category")
router.register(r'priorities', PriorityViewSet, basename="priority")
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
]
