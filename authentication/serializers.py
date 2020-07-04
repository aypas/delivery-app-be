from rest_framework import serializers
from authentication.models import CustomUser
from business_logic.models import Node 

class NS(serializers.ModelSerializer):
	class Meta:
		model = Node 
		fields = ['id', 'name']

class UserMetaSerializer(serializers.ModelSerializer):
	of_node = NS(many=True)
	class Meta:
		model = CustomUser
		fields = ['id', 'is_active', 'email',
				  'name', 'created', 'is_node_owner',
				  'status', 'on_shift', 'is_manager',
				  'of_node']

		read_only_fields = ['email', 'of_node']

class UserSimpleNestedSerializer(serializers.ModelSerializer):
	class Meta:
		model = CustomUser
		fields = ['id', 'name', 'of_node']

class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = CustomUser
		fields = ['id', 'name', 'email']