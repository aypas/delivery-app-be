from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny


from django.db.models import Count, Case, When, IntegerField
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

from authentication.permissions import IsNodeOwnerOrManager
from .models import Node, Partner, Order 
from .serializers import (NodeSerializer as NS,
						  PartnerSerializer as PS,
						  PartnerPutSerializer,
						  OrderSerializer as OS)


from .datetime_utils import make_datetime_object
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

class ChangeUserPermissions(APIView):
	permission_classes = [IsAuthenticated,]
	
	def get_object(self, node_pk, user_pk, permission):
		if permission == "worker":
			Node.workers.through.objects.filter(node_id=node_pk, customuser_id=user_pk)
		if permission == "manager":
			Node.managers.through.objects.filter(node_id=node_pk, cutomuser_id=user_pk)
		if permission == "owner":
			pass
			#ensure requestor is creator

	def post(self, request, node_pk, user_pk, permission):
		print(request.META)
		return Response({'data': 'kaka'}, status=status.HTTP_200_OK)

	def delete(self, node_pk, user_pk, permission):
		pass

class OrderView(APIView):

	permission_classes = [IsAuthenticated,]
	'''
	accepted query strings: 
	complete:[true or false], 
	in_progress=[true or false], 
	time=datestring, converted to an datetime obj,

	client must send querystring params as json encoded object
	
	permissions will get very confusing as workers are added...
	eg, a user with worker permissions is only allowed to change in_progress and complete

	'''
	def parse_query_string(self, query_string):
		qs = json.loads(urllib.parse.unquote(query_string))
		qs['entry_date__gt'] = make_datetime_object(qs['time'])
		del qs['time']
		return qs
	def get_data(self, pk, request=None):
		if request != None:
			qs = self.parse_query_string(request.META['QUERY_STRING'])
			return Order.objects.filter(store__of_node=pk, **qs)
		try:
			return Order.objects.filter(pk=pk)
		except ObjectDoesNotExist as e:
			raise e

	def get(self, request, pk):
		#gets many, pk represents id of node
		serializer = OS(self.get_data(pk, request=request), many=True)
		return Response(serializer.data, status=status.HTTP_200_OK)

	def put(self, request, pk):
		#updates 1, pk represents id of order
		try:
			print(request.data)
			if request.data.get('deliver_by', None):
				request.data['deliver_by'] = make_datetime_object(request.data['deliver_by'])
			self.get_data(pk).update(**request.data)
			return Response(request.data, status=status.HTTP_200_OK)
		except Exception as e:
			print(e)
			return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)

class PartnerView(APIView):
	#since a user can own multiple nodes, these views have a pk passed
	permission_classes = [IsAuthenticated, IsNodeOwnerOrManager]
	def get_objects(self, pk, single=False):
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
		#pk is pk of node to which partner belongs
		f = PS(self.get_objects(pk), many=True)
		return Response(f.data, status=status.HTTP_200_OK)

	def post(self, request, pk):
		#pk is pk of node to which resource belongs
		print(request.data)
		serializer = PS(data={**request.data, 'of_node': pk})
		print(serializer.is_valid())
		if serializer.is_valid():
			print('valid')
			serializer.save()
			return Response(serializer.data, status=status.HTTP_200_OK)
		print(serializer.errors, request.data.get('other_names'))
		return Response({"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

	def put(self, request, pk):
		#pk means pk of resource being updated
		print('userless', request.data)
		obj = self.get_objects(pk, single=True)
		if not obj:
			return Response({"detail": "nothing in our database matches the given id"}, status=status.HTTP_404_NOT_FOUND)
		serializer = PartnerPutSerializer(instance=obj, data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_200_OK)
		print(type(serializer.errors), serializer.errors)
		return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
	def delete(self, request, pk):
		print(request.data)
		update = Partner.objects.filter(pk=pk).update(active=request.data["active"])
		if update:
			return Response({"detail": "success"}, status=status.HTTP_200_OK)
		else:
			return Response({"detail": "a partner with the given id was not found"}, status=status.HTTP_404_NOT_FOUND)

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