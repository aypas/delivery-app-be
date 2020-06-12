import os
import google.oauth2.credentials
import google_auth_oauthlib.flow

flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
		    		os.path.join(os.path.dirname(__file__), 'client_secret.json'),
		    		scopes=["https://www.googleapis.com/auth/gmail.readonly"],
		    		redirect_uri = "https://api.a-delivery.tk/api/auth/oauth2callback/"
		    )
