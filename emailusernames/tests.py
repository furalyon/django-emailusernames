from django.test import TestCase
from .models import User

class UserTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create(
            email='q@w.er',password='12345',email_verified=True)
