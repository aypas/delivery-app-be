from django.http import JsonResponse
from delivery_app.settings import SECRET_KEY
import hashlib

#406=not acceptable
class PermissionsVerification:
	def __init__(self, get_response):
		self.get_response = get_response
		self.secret_key = SECRET_KEY.encode('utf-8')
		self.response = (JsonResponse({'detail': 'You\'re missing your signed cookie'}, status=406),
						 JsonResponse({'detail': 'very sketchy shit'}, status=406))

	def __call__(self, request):
		response = self.get_response(request)
		return response

	def process_view(self, request, view_func, view_args, view_kwargs):
		sign = request.COOKIES.get('permissions_sign', None)
		perms = request.META.get('HTTP_PERMISSIONS', None)
		print(perms)
		if perms == None:
			return None
		elif perms != None and sign == None:
			print('''a signed cookie is required when permissions verfication middleware 
					   is active and HTTP_PERMISSIONS are sent''')
			return self.response[0]
		hasher = hashlib.sha1()
		hasher.update(self.secret_key)
		hasher.update(perms.encode('utf-8'))
		print(hasher.hexdigest(), sign)
		if hasher.hexdigest() != sign:
			print('sign and given permissions do not match')
			return self.response[1]
		return None