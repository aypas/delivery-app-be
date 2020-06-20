from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, throttle_classes, permission_classes


from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

from authentication.misc import flow
from authentication.permissions import IsNodeOwnerOrManager, IsSoleNodeOwner
from authentication.serializers import UserMetaSerializer as US, UserSerializer

from business_logic.models import Node

#needs User for owner/manager
#needs User for self
#needs Users for owner/manager
#needs Users for self---maybe

#thats it...



class SignUp(APIView):

	def get_object(self, code):
		try:
			return Node.objects.get(code=code).pk

		except:
			return false
	def post(self, request):
		model = get_user_model()(name=request.data.get('name'),
							   email=request.data.get('email'))

		node = self.get_object(request.data.get('code'))
		if node:
			model.set_password(request.data.get('password'))
			model.save()
			model.of_node.add(node)
			return Response({"status": status.HTTP_200_OK, "data": US(model).data})
		return Response({"status": status.HTTP_400_BAD_REQUEST, "error": us.errors})


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
			return Response({"status": status.HTTP_200_OK, "data": data.data})
		return Response({"status": status.HTTP_400_BAD_REQUEST, "error": data.errors})



class UsersOfNode(APIView):
	permission_classes = [IsAuthenticated, IsNodeOwnerOrManager]
	#should serve users of requestor's node

	def get(self, request, cflow, nodePk):
		cflow = cflow.lower()
		if cflow == "owners":
			users = Node.objects.get(pk=nodePk).co_owners.all()
			print('hello?')
			serial = US(users, many=True)
			return Response({'data': serial.data, 'status': status.HTTP_200_OK})
		elif cflow == "managers":
			serial = US(Node.objects.get(pk=nodePk).managers.all(), many=True)
			return Response({'data': serial.data, 'status': status.HTTP_200_OK})
		elif cflow == "workers":
			serial = US(Node.objects.get(pk=nodePk).workers.all(), many=True)
			return Response({'data': serial.data, 'status': status.HTTP_200_OK})
		else:
			return Response({"status": status.HTTP_404_NOT_FOUND})
		
@api_view(["GET"])
@permission_classes([IsSoleNodeOwner])
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
		auth_code = request.GET.get('code')
		print(request.GET.get('state'))
		flow = flow.fetch_token(code=auth_code)
		creds = flow.credentials
		if not creds.refresh_token:
			print( '''Something went wrong. We need you to delete any permissions
											you\'ve given us and try again''')
			return Response({'status': 'fail', 
							'detail': 'something went wrong on google\'s end. Please try again.'})

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
		return HttpResponseRedirect("http://a-delivery.tk/dashboard?success/")
		#redirect(a-delivery.tk/success...)

	except Exception as e:
		print(e)
		return Response({'status': 'fail'})


