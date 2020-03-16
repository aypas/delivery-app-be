from django.db import models
from django.contrib.auth.models import AbstractUser
from authentication.managers import CustomUserManager

# Create your models here.
class CustomUser(AbstractUser):

	STATUSES = [('av', 'available',), ('unv','unavailable',)]

	username = models.CharField(max_length=25, blank=True, unique=False, default='')
	id = models.AutoField(primary_key=True)
	email = models.EmailField(unique=True, blank=False, max_length=50)
	name = models.CharField(max_length=55)
	password = models.CharField(max_length=100)
	created = models.DateField(auto_now_add=True)
	status = models.CharField(max_length=20, choices=STATUSES, default="unv")
	on_shift = models.BooleanField(default=False)
	is_manager = models.BooleanField(default=False)
	is_node_owner = models.BooleanField(default=False)

	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = []

	objects = CustomUserManager()

	def __str__(self):
		return self.email
		
	def __repr__(self):
		return f"<object {self.email} @ {id(self)}>"