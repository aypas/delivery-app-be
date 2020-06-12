from rest_framework import serializers
from authentication.models import CustomUser

class UserMetaSerializer(serializers.ModelSerializer):

	class Meta:
		model = CustomUser
		fields = ['id', 'is_active', 'email',
				  'name', 'created', 'is_node_owner',
				  'status', 'on_shift', 'is_manager']

class UserSimpleNestedSerializer(serializers.ModelSerializer):
	class Meta:
		model = CustomUser
		fields = ['id', 'name']

class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = CustomUser
		fields = '__all__'