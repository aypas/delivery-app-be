from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, throttle_classes, permission_classes

from rest_framework_simplejwt.views import TokenObtainPairView

from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

from authentication.misc import flow
from authentication.permissions import IsNodeOwnerOrManager, IsSoleNodeOwner
from authentication.serializers import (UserMetaSerializer as US,
										UserAndTokenPairObtainSerializer)


from business_logic.models import Node

#every single error message needs to respond with {"status" 4.., "detail": "something" }
#which amounts to Response({"detail": "thing"}, status=HTTP_4...)
#catch on axios with error.response 



class SignUp(APIView):

	def get_object(self, code):
		try:
			return Node.objects.get(code=code).pk

		except:
			return False
	def post(self, request):
		model = get_user_model()(name=request.data.get('name'), email=request.data.get('email'))
		code = request.data.get('code', None)
		print(request.data)
		if code == 123456:
			model.is_node_owner = True
			model.is_manager = True
			model.set_password(request.data.get('password'))

			try:
				model.save()
				return Response(US(model).data, status=status.HTTP_200_OK)
			except IntegrityError as e:
				return Response({"detail": "an account with that email already exists"}, status=status.HTTP_400_BAD_REQUEST)
		else:
			node = self.get_object(code)
			if not node:
				return Response({"detail": 'the provided code is not valid for any business on our system'},
								status=status.HTTP_400_BAD_REQUEST)
			model.set_password(request.data.get('password'))

			try:
				model.save()
				model.of_node.add(node)
				return Response({"data": US(model).data}, status=status.HTTP_200_OK)
			except IntegrityError as e:
				return Response({"detail": "an account with that email already exists"}, status=status.HTTP_400_BAD_REQUEST)

class TokenObtainPair(TokenObtainPairView):
	serializer_class = UserAndTokenPairObtainSerializer


class User(APIView):

	permission_classes = [IsAuthenticated,]

	def get_object(self, email):
		
		try:
			return get_user_model().objects.get(email=email)

		except Exception as e:
			return e
	def get(self, request):
		serializer = US(self.get_object(email=request.user))
		return Response(serializer.data)

	def put(self, request):
		obj = self.get_object(request.user)
		data = US(obj, data=request.data, partial=True)
		if data.is_valid():
			data.save()
			return Response(data.data, status=status.HTTP_200_OK)
		return Response({"detail": data.errors}, status=status.HTTP_400_BAD_REQUEST)



class UsersOfNode(APIView):
	permission_classes = [IsAuthenticated, IsNodeOwnerOrManager]
	#should serve users of requestor's node

	def get(self, request, cflow, nodePk):
		cflow = cflow.lower()
		if cflow == "owners":
			users = Node.objects.get(pk=nodePk).co_owners.all()
			print('hello?')
			serial = US(users, many=True)
			return Response({'data': serial.data}, status=status.HTTP_200_OK)
		elif cflow == "managers":
			serial = US(Node.objects.get(pk=nodePk).managers.all(), many=True)
			return Response({'data': serial.data},status=status.HTTP_200_OK)
		elif cflow == "workers":
			serial = US(Node.objects.get(pk=nodePk).workers.all(), many=True)
			return Response({'data': serial.data}, status=status.HTTP_200_OK)
		else:
			return Response({"detail": f"trailing /{cflow} is not valid"}, status=status.HTTP_404_NOT_FOUND)
		
@api_view(["GET"])
@permission_classes([IsSoleNodeOwner])
def init(request):
	url, _ = flow.authorization_url(
				access_type='offline',
			    # Enable incremental authorization. Recommended as a best practice.
			    include_granted_scopes='true')
	
	return Response({ 'url': url}, status=status.HTTP_200_OK)



@api_view(["GET", "POST"])
def Oauth2Callback(request):
	#if fail, instuct user to to https://myaccount.google.com/permissions,
	#delete any granted permission, and try again
	try:
		auth_code = request.GET.get('code')
		print(request.GET.get('state'), 'is it working?')
		flow.fetch_token(code=auth_code)
		creds = flow.credentials
		if not creds.refresh_token:
			print( '''Something went wrong. We need you to delete any permissions
											you\'ve given us and try again''')
			return Response({'detail': 'something went wrong on google\'s end. Please try again.'},
							status=status.HTTP_400_BAD_REQUEST)#change to apropriate code

		oauth = {
				  'scopes': creds.scopes, 
				  'client_secret': creds.client_secret,
				  'token_uri': creds.token_uri,
				  'id_token': creds.id_token,
				  'client_id': creds.client_id,
				  'token': creds.token,
				  'refresh_token': creds.refresh_token
				  										}

		node = Node.objects.filter(owner__email=request.user).update(oauth=oauth)
		print(user.oauth)
		user.save()
		return Response({"data": "succesfully linked your gmail account"}, status=status.HTTP_200_OK)

	except Exception as e:
		print(e)
		return Response({'detail': 'fail'}, status=status.HTTP_400_BAD_REQUEST)


