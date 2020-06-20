from django.db import models
from authentication.models import CustomUser
from business_logic.misc import timezone #fucked
from django.contrib.postgres.fields import JSONField


class Node(models.Model):
	#on node creation, owner must be added to co_owners as well...
	name = models.CharField(max_length=30, blank=True)
	owner = models.OneToOneField(CustomUser, related_name='owner', on_delete=models.PROTECT)
	co_owners = models.ManyToManyField(CustomUser, related_name='owners')
	managers = models.ManyToManyField(CustomUser, related_name='managers', limit_choices_to={'is_manager': True},)
	workers = models.ManyToManyField(CustomUser, related_name='workers') 
	address = models.CharField(max_length=255)
	code = models.IntegerField()
	oauth = JSONField(blank=True, null=True)


	def __str__(self):
		return self.name



class Partner(models.Model):

	of_node = models.ForeignKey(Node, null=True, on_delete=models.SET_NULL) #change name holy s!
	name = models.CharField(max_length=255)
	street_address = models.CharField(max_length=255)
	active = models.BooleanField(default=True)
	email = models.EmailField(blank=True)#not sure if emailfield is needed, not sure if itll match a string tbh

	def __str__(self):
		return self.name


class Order(models.Model):

	store = models.ForeignKey(Partner, related_name='store', null=True, blank=True, on_delete=models.SET_NULL)
	assigned_to = models.ForeignKey(CustomUser, blank=True, null=True,
									related_name='assigned_user', on_delete=models.SET_NULL)


	html = models.TextField(blank=True)
	result = models.CharField(blank=True, max_length=20)
	source = models.CharField(max_length=30, blank=True)
	customer_phone=models.CharField(max_length=30)
	order_number = models.CharField(max_length=200, unique=True)
	name = models.CharField(max_length=200)
	address = models.CharField(max_length=300)
	deliver_by = models.CharField(max_length=200)
	entry_date = models.DateTimeField(auto_now_add=True)#change default to aware object with tz=est time...	
	total_price = models.DecimalField(max_digits=6, decimal_places=2)
	tip = models.DecimalField(max_digits=6, decimal_places=2)
	delivery_fee = models.DecimalField(max_digits=6, decimal_places=2)#need to fix some views...ive been using total price for each time
	note = models.CharField(max_length=300, blank=True)

	in_progress = models.BooleanField(default=False)
	complete = models.BooleanField(default=False)
	completed_time = models.DateTimeField(blank=True, null=True)



	def __str__(self):
		return self.store.name