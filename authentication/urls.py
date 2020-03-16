from django.urls import path
from rest_framework_simplejwt import views as jwt_views
from authentication.views import (User, Users, HW)

urlpatterns = [

		path('user/', User.as_view(), name="get_user"),
		path('users/', Users.as_view(), name="users"),
		path('hw/', HW.as_view(), name="hw"),

		path('token/', jwt_views.TokenObtainPairView.as_view(), name="token_obtain_pair"),
		path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name="token_refresh"),
	]