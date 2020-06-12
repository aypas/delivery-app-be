from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view, throttle_classes

from authentication.serializers import UserMetaSerializer as US, UserSerializer

from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

from authentication.misc import flow

@api_view(["POST"])
def SignUp(request):
	us = UserSerializer(data=request.data)
	if err:=us.is_valid():
		us.save()
		return Response({"status": status.HTTP_200_OK})
	print(r)
	return Response({"status": status.HTTP_400_BAD_REQUEST, "error": err})


class User(APIView):

	permission_classes = [IsAuthenticated,]

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

	def get_objects(self, **parameters):
		print(parameters)
		return get_user_model().objects.all()

	def get(self, request):
		print(request)
		print(request.GET, type(request.GET),request.GET.__dict__)
		serializer = US(self.get_objects(**request.GET.__dict__), many=True)
		return Response(serializer.data)
		
@api_view(["GET"])
def init(request):
	url, _ = flow.authorization_url(

				access_type='offline',
			    # Enable incremental authorization. Recommended as a best practice.
			    include_granted_scopes='true'

		)
	
	return Response({ 'url': url})

@api_view(["GET", "POST"])
def oauth2callback(request):

	try:
		user = Node.objects.get(managers__user__email=request.user)

		auth_code = request.GET.get('code')

		print(request.GET.get('state'))

		flow = flow.fetch_token(code=auth_code)
		
		creds = flow.credentials

		if not creds.refresh_token:
			print( '''Something went wrong. We need you to delete any permissions
											you\'ve given us and try again''')
			return Response({'status': 'fail'})

		user.oauth = {
					  'scopes': creds.scopes, 
					  'client_secret': creds.client_secret,
					  'token_uri': creds.token_uri,
					  'id_token': creds.id_token,
					  'client_id': creds.client_id,
					  'token': creds.token,
					  'refresh_token': creds.refresh_token
					  										}


		print(user.oauth)
		user.save()
		return Response({'status': 'success'})

	except Exception as e:
		print(e)
		return Response({'status': 'fail'})


