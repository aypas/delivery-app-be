from rest_framework import permissions
from .models import CustomUser

class IsNodeOwnerOrManager(permissions.BasePermission):
	def has_permission(self, request, view):
		print('IsNodeOwnerOrManager has run')
		model = CustomUser.objects.values('is_manager', 'is_node_owner').get(email=request.user)
		if model['is_manager'] or model['is_node_owner']:
			return True
		return False

class IsNodeOwner(permissions.BasePermission):
	def has_permission(self, request, view):
		print('IsNodeOwner has run')
		owner = CustomUser.objects.get(email=request.user).is_node_owner
		if owner:
			return True
		return False

class IsSoleNodeOwner(permissions.BasePermission):
	def has_permission(self, request, view):
		print('IsSoleNodeOwner has run')
		try:
			owner = Node.objects.get(owner__email=request.user)
			return True
		except:
			return False
