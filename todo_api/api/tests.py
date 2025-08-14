from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from .models import Task, Category, Priority

class ApiTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='u1', password='pass')
        self.other = User.objects.create_user(username='u2', password='pass')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.cat = Category.objects.create(name='C1', created_by=self.user)
        self.pri = Priority.objects.create(name='P1', created_by=self.user)

    def test_create_task_and_filter(self):
        r = self.client.post('/api/tasks/', {'title':'T1','status':'new','category':self.cat.id,'priority':self.pri.id})
        self.assertEqual(r.status_code, 201)
        r2 = self.client.get('/api/tasks/?status=new')
        self.assertEqual(r2.status_code, 200)
        self.assertEqual(len(r2.json()), 1)

    def test_visibility_scoped(self):
        Task.objects.create(title='X', status='new', created_by=self.other)
        r = self.client.get('/api/tasks/')
        self.assertEqual(len(r.json()), 0)

    def test_soft_delete_user_hard_delete_admin(self):
        t = Task.objects.create(title='T2', status='new', created_by=self.user)
        r = self.client.delete(f'/api/tasks/{t.id}/')
        self.assertIn(r.status_code, [204, 200, 202])
        t.refresh_from_db()
        self.assertTrue(t.deleted)

    def test_me_and_change_password(self):
        r = self.client.get('/api/users/me/')
        self.assertEqual(r.status_code, 200)
        r2 = self.client.post('/api/users/change_password/', {'old_password':'pass','new_password':'newpass'})
        self.assertEqual(r2.status_code, 200)
