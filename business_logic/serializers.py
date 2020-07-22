from rest_framework import serializers
from authentication.serializers import UserMetaSerializer, UserSimpleNestedSerializer
from .models import Node, Partner, Order

class NodeSerializer(serializers.ModelSerializer):
	owner = UserSimpleNestedSerializer(read_only=True)
	managers = UserSimpleNestedSerializer(many=True, read_only=True)
	co_owners = UserSimpleNestedSerializer(many=True, read_only=True)
	workers = UserSimpleNestedSerializer(many=True, read_only=True)
	class Meta:
		model = Node
		fields = "__all__"


class PartnerSerializer(serializers.ModelSerializer):
	class Meta:
		model = Partner
		fields = "__all__"

class PartnerPutSerializer(serializers.ModelSerializer):
	class Meta:
		model = Partner
		fields = "__all__"
		read_only_fields = ["of_node"]

class OrderSerializer(serializers.ModelSerializer):
	assigned_to = UserSimpleNestedSerializer()
	store = PartnerSerializer()
	last_edited_by = UserSimpleNestedSerializer()
	class Meta:
		model = Order
		fields = "__all__"
		read_only_fields = ['id', 'store']