#from django.contrib.auth import authenticate
from rest_framework import exceptions, serializers

from rest_framework_simplejwt.serializers import TokenObtainSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from authentication.models import CustomUser
from business_logic.models import Node



ATTRS = ['id', 'is_active', 'email',
		 'name', 'created', 'is_node_owner',
		 'status', 'on_shift', 'is_manager',
		 'email',]

class NS(serializers.ModelSerializer):
	class Meta:
		model = Node 
		fields = ['id', 'name']

class UserMetaSerializer(serializers.ModelSerializer):
	of_node = NS(many=True)
	class Meta:
		model = CustomUser
		fields = ATTRS + ['of_node']
		read_only_fields = ['email', 'of_node']

class UserSimpleNestedSerializer(serializers.ModelSerializer):
	class Meta:
		model = CustomUser
		fields = ['id', 'name', 'email']

class UserAndTokenPairObtainSerializer(TokenObtainSerializer):
	@classmethod
	def get_token(cls, user):
		return RefreshToken.for_user(user)

	def validate(self, attrs):
		authenticate_kwargs = {self.username_field: attrs[self.username_field], 'password': attrs['password']}

		try:
		    authenticate_kwargs['request'] = self.context['request']
		except KeyError:
		    pass

		user = CustomUser.authenticate(**authenticate_kwargs)
		if user is None or not user.is_active:
		    raise exceptions.AuthenticationFailed(
		        self.error_messages['no_active_account'],
		        'no_active_account',
		    )
		else:
			user_dict = dict()
			for attr in ATTRS:
				user_dict[attr] = user.__getattribute__(attr)
			user_dict['of_node'] = CustomUser.determine_permissions(authenticate_kwargs['email'], user)
		
		refresh = self.get_token(user)

		return {'user': user_dict, 
				'tokens': {'refresh': str(refresh), 'access': str(refresh.access_token)}}