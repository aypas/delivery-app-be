from rest_framework import permissions
from authentication.models import CustomUser
import json

def deserialize(perms):
	return json.loads(perms)

def find_relevant_perms(perms, pk):
	for perm in perms:
		if perm['id'] == pk:
			return perm
	return None

def get_perms(request):
	str_perms = request.META.get('HTTP_PERMISSIONS', None)
	pk = request.resolver_match.kwargs.get('node_pk', None)
	if str_perms == None or pk == None:
		print(f"pk was sent: {pk != None}, perms were sent: {str_perms != None}.")
		print("both are needed for the given url.")
		return None
	return find_relevant_perms(deserialize(str_perms), pk)

class IsNodeWorker(permissions.BasePermission):
	def has_permission(self, request, view):
		perms = get_perms(request)
		if perms == None:
			return False
		if perms['worker']:
			return True
		return False

class IsNodeOwnerOrManager(permissions.BasePermission):
	def has_permission(self, request, view):
		perms = get_perms(request)
		if perms == None:
			return False
		if perms['owner'] or perms['manager']:
			return True
		return False

class IsNodeOwner(permissions.BasePermission):
	def has_permission(self, request, view):
		print('IsSoleNodeOwner has run')
		perms = get_perms(request)
		if perms == None:
			return False
		if perms['owner']:
			return True
		return False