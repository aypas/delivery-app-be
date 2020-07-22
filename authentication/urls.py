from django.urls import path
from rest_framework_simplejwt import views as jwt_views
from authentication.views import (User, UsersOfNode, SignUp,
								  init, Oauth2Callback, TokenObtainPair)

urlpatterns = [

		path('user/', User.as_view(), name="get_user"),
		path('users/<str:cflow>/<int:nodePk>', UsersOfNode.as_view(), name="users"),
		path('signup/', SignUp.as_view(), name="signup"),
		path('token/', TokenObtainPair.as_view(), name="token_obtain_pair"),
		path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name="token_refresh"),

		path('oauth/', init, name='oauth'),
		path('callback/', Oauth2Callback, name='callback')
	]