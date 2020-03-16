from rest_framework import serializers
from authentication.serializers import UserMetaSerializer, UserSimpleNestedSerializer
from .models import Node, Partner, Order

class NodeSerializer(serializers.ModelSerializer):
	managers = UserMetaSerializer(many=True, read_only=True)
	owner = UserMetaSerializer(read_only=True)
	class Meta:
		model = Node
		fields = "__all__"


class PartnerSerializer(serializers.ModelSerializer):
	class Meta:
		model = Partner
		fields = "__all__"


class OrderSerializer(serializers.ModelSerializer):
	assigned_to = UserSimpleNestedSerializer()
	class Meta:
		model = Order
		fields = "__all__"