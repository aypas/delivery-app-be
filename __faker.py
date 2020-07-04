import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE","delivery_app.settings")
django.setup()

import sys
import random
import datetime as dt
from faker import Faker
from authentication.models import CustomUser
from business_logic.models import Node, Partner, Order


def node(n=0):
	faker = Faker()
	f = range(0, CustomUser.objects.count())
	
	for _ in range(n):

		r = CustomUser.objects.all()[1]
		try:
			node = Node()
			node.owner=r
			node.address=faker.address()
			node.save()
			node.managers.add(r)
			node.save()

		except Exception as e:
			print(e)
			continue

def order(n):
	print(str(n))
	f=Partner.objects.all().count()
	faker = Faker()

	if not f:
		raise Exception("must have at least one partner before you can create an Order")

	for _ in range(f):

		try:
			Order.objects.create(store=Partner.objects.all()[random.choice(range(0,f))],
									assigned_to=None, source=random.choice(['grubhub', 'doordash', 'chownow']),
									customer_phone=faker.phone_number(), order_number=random.choice(range(1,100000)), name=faker.name(),
									address=faker.address(), deliver_by=dt.datetime.now()+dt.timedelta(hours=1),
									total_price=random.choice([28.92, 42.55, 21.11]), tip=random.choice([3.00, 2.55, 5.01]), delivery_fee=3.00)

		except Exception as e:
			print(e)
			continue

def partner(n):
	faker = Faker()

	for _ in range(n):
		try:
			Partner.objects.create(of_node_id=9,
						   name = faker.company(),
						   street_address=faker.address())
		except Exception as e:
			print(e)
			continue

if __name__ == "__main__":

	#script node=3 order=3 partner=6
	for i in sys.argv:
		if i==__file__:
			continue

		arg = i.split('=')

		if arg[0]=="node":
			node(int(arg[1]))
		elif arg[0]=="order":
			order(int(arg[1]))
		elif arg[0]=="partner":
			partner(int(arg[1]))
		else:
			print("There's a typo in one of your args")