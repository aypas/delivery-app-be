from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny

from authentication.serializers import UserMetaSerializer as US 
from django.contrib.auth import get_user_model
#from rest_framework_simplejwt.authentication import JWTAuthentication as i


class User(APIView):

	permission_classes = [IsAuthenticated,]
	#authentication_classes = [i,]

	def get_object(self, email):
		
		try:
			return get_user_model().objects.get(email=email)

		except Exception as e:
			print(e)#bad!!!

	def get(self, request):
		print(request.META)
		serializer = US(self.get_object(email=request.user))
		return Response(serializer.data)

	def post(self, request):
		pass

	def put(self, request):
		pass

	def delete(self, request):
		pass



class Users(APIView):
	permissions_classes = [IsAuthenticated,]
	#authentication_classes = [i,]

	def get_objects(self, **parameters):
		print(parameters)
		return get_user_model().objects.all()

	def get(self, request):
		print(request)
		print(request.GET, type(request.GET),request.GET.__dict__)
		serializer = US(self.get_objects(**request.GET.__dict__), many=True)
		return Response(serializer.data)
		

class HW(APIView):
	permission_classes = [IsAuthenticated,]

	def get(self, request):
		print(request.META)
		return Response({"msg": "Hello World"})
