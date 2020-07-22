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
	of_node = models.ManyToManyField('business_logic.Node')

	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = []

	objects = CustomUserManager()

	def __str__(self):
		return self.email
		
	def __repr__(self):
		return f"<object {self.email} @ {id(self)}>"

	@classmethod
	def authenticate(cls, request, email=None, password=None):
		print("running custom")
		if email is None or password is None:
		    return
		try:
		    user = cls.objects.prefetch_related('of_node__managers', 
		    									'of_node__co_owners', 
		    									'of_node__workers')\
		    				   .get(email=email)
		except cls.DoesNotExist:
		    # Run the default password hasher once to reduce the timing
		    # difference between an existing and a nonexistent user (#20760).
		    cls().set_password(password)
		else:
		    if user.check_password(password) and user.is_active:
		        return user
	@classmethod
	def determine_permissions(cls, email, query):
		return_list = list()
		if not query.is_node_owner and not query.is_manager:
			for i in query.of_node.all():
				print("caught by first if at determine_permissions")
				return_list.append({"owner": False, "manager": False, "worker": True})
			return return_list
		
		for node in query.of_node.all():
			node_dict = {"id": node.id, "name": node.name}
			#naively assume everyone has worker permission on site
			node_dict['worker'] = True
			for owner in node.co_owners.all():
				if email == owner.email:
					node_dict['owner'] = True
					break
			if node_dict.get('owner', None):
				node_dict['manager'] = True
				node_dict['worker'] = True
				return_list.append(node_dict)
				continue
			else:
				node_dict['owner'] = False
				for manager in node.managers.all():
					if email == manager.email:
						node_dict['manager'] = True
						break
				if not node_dict.get('manager', None):
					node_dict['manager'] = False
				return_list.append(node_dict)
		return return_list