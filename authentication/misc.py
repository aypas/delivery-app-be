import os, hashlib, json
import google.oauth2.credentials
from google_auth_oauthlib.flow import Flow
from delivery_app.settings import SECRET_KEY

flow = Flow.from_client_secrets_file(os.path.join(os.path.dirname(__file__), 'client_secret.json'),
		    						 scopes=["https://www.googleapis.com/auth/gmail.readonly",
		    								 "https://www.googleapis.com/auth/gmail.modify"],
		    						 redirect_uri = "https://a-delivery.tk/callback")

def sign_permissions(response):
	string = json.dumps(response.data['user']['of_node'], separators=(',', ':'))
	print(string)
	hasher = hashlib.sha1()
	hasher.update(SECRET_KEY.encode('utf-8'))
	hasher.update(string.encode('utf-8'))
	return hasher.hexdigest()