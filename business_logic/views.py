from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny


from django.db.models import Count, Case, When, IntegerField
from django.contrib.auth import get_user_model
from authentication.permissions import IsNodeOwnerOrManager
from .models import Node, Partner, Order 
from .serializers import (NodeSerializer as NS,
						  PartnerSerializer as PS,
						  OrderSerializer as OS)

import json, urllib
#every single error message needs to respond with {"status" 4.., "detail": "something" }
#which amounts to Response({"detail": "thing"}, status=HTTP_4...)
#catch on axios with error.response

class NodeView(APIView):
	permission_classes = [IsAuthenticated, IsNodeOwnerOrManager]

	def get_object(self, pk):
		return Node.objects.get(pk=pk)

	def get(self, request, pk):
		print(self.get_object(pk))
		return Response(NS(self.get_object(pk)).data)
		#return Response({"detail": "shit"}, status=status.HTTP_400_BAD_REQUEST)

	def post(self, request, pk):
		try:
			print(request.data)
			node = Node(**request.data, owner_id=pk)
			node.save()
			node.co_owners.add(pk)
			node.managers.add(pk)
			node.workers.add(pk)
			get_user_model().objects.get(pk=pk).of_node.add(node.pk)
			serializer = NS(node)
			return Response(serializer.data, status=status.HTTP_200_OK)
		except Exception as e:
			print(e)
			return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


	def put(self, request, pk):
		data = NS(instance=self.get_object(pk), data=request.data, partial=True)
		print(request.data.get('code'))
		if data.is_valid():
			print(request.data.get('code'), data.validated_data.get('code'))
			data.save()
			return Response(data.data, status=status.HTTP_202_ACCEPTED)
		return Response({'detail': data.errors}, status=status.HTTP_400_BAD_REQUEST)

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

class PartnerView(APIView):
	#since a user can own multiple nodes, these views have a pk passed
	permission_classes = [IsAuthenticated, IsNodeOwnerOrManager]
	def get_objects(self, pk, single=False ):
		if single:
			try:
				return Partner.objects.get(pk=pk)
			except Exception as e:
				return False

		else:
			f=Partner.objects.filter(of_node=pk)
			print(len(f))
			return f
	def get(self, request, pk):
		f = PS(self.get_objects(pk), many=True)
		return Response(f.data, status=status.HTTP_200_OK)

	def post(self, request, pk):
		#manually have to add of_node
		f = PS(data=request.data)
		print(f.is_valid())
		if f.is_valid():
			print('valid')
			f.save()
			return Response(f.data, status=status.HTTP_200_OK)
		return Response({"detail": f.errors}, status=HTTP_400_BAD_REQUEST)

	def put(self, request, pk):
		print('userless', request.data)
		obj = self.get_objects(pk, single=True)
		if not obj:
			return Response({"detail": "nothing in our database matches with the given id"}, status=status.HTTP_404_NOT_FOUND)
		serializer = PS(instance=obj, data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_200_OK)
		return Response({"detail": serializer.errors}, status.HTTP_400_BAD_REQUEST)



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