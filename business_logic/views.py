from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny

from .QStringParsers import OrderViewQString
from django.db.models import Count, Case, When, IntegerField
from django.contrib.auth import get_user_model

from .models import Node, Partner, Order 
from .serializers import (NodeSerializer as NS,
						  PartnerSerializer as PS,
						  OrderSerializer as OS,)

import json, urllib


class NodeView(APIView):
	#permission_classes = [IsAuthenticated,]


	#idk what im really doing with this view
	#i can edit a node through admin
	#only one's self should be able to really edit a node really...so wtf with the pk
	#kinda my first view in a long time
	# ...

	def get_object(self, pk):
		return get_object_or_404(Node, pk=pk)

	def get(self, request, pk):
		print(request.user)
		return Response(NS(self.get_object(pk)).data)


	def put(self, request):
		data = NS(instance=self.get_object(request.user), data=request.data)
		print(data)

		if data.is_valid():
			data.save()
			return Response(data.data, status=status.HTTP_202_ACCEPTED)
		return Response(data.errors, status=status.HTTP_400_BAD_REQUEST)

class OrderView(APIView):
	'''
	accepted query strings: 
	complete:[true or false], 
	in_progress=[true or false], 
	store=[variable],

	client must send params as json

	'''
	#permission_classes = [IsAuthenticated,]

	def get_data(self, request):

		if r:=request.META['QUERY_STRING']:
			print(json.loads(urllib.parse.unquote(r)))
			return Order.objects.filter(**json.loads(urllib.parse.unquote(r)))
		return Order.objects.all()

	def get(self, request):
		print(request.META)
		serializer = OS(self.get_data(request), many=True)
		return Response(serializer.data, status=status.HTTP_200_OK)


	#user put for assign, post for edits

class OrderCountView(APIView):

	def data(self):

		order = Order.objects.all()\
							 .aggregate(total_unassigned=Count(Case(When(assigned_to=None,then=1),
							            output_field=IntegerField())),
										
										total_pending=Count(Case(When(assigned_to__isnull=False, 
									    in_progress=False, complete=False, then=1),output_field=IntegerField())),

									    total_in_progress=Count(Case(When(assigned_to__isnull=False, 
									    in_progress=True, complete=False, then=1),output_field=IntegerField()))
									    )
		shift = get_user_model().objects.all()\
										   .aggregate(on=Count(Case(When(on_shift=True, then=1)),
											          output_field=IntegerField()))

		return {**shift, **order}


	def get(self, request):
		return Response(self.data())