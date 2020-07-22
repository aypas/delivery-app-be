import os
import google.oauth2.credentials
from google_auth_oauthlib.flow import Flow

flow = Flow.from_client_secrets_file(
		    os.path.join(os.path.dirname(__file__), 'client_secret.json'),
		    scopes=["https://www.googleapis.com/auth/gmail.readonly",
		    		"https://www.googleapis.com/auth/gmail.modify"],
		    redirect_uri = "https://a-delivery.tk/callback")
