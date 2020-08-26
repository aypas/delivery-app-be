from django.urls import path
from .views import (NodeView, OrderView, OrderCountView,
					PartnerView, ChangeUserPermissions)

urlpatterns = [

	path('node/<int:pk>/', NodeView.as_view(), name="tbd"),
	path('orders/<int:pk>/', OrderView.as_view(), name="idk"),
	path('counts/', OrderCountView.as_view(), name='nullll'),
	path('partners/<int:pk>/', PartnerView.as_view(), name='partner'),
	path(r'permissions/<str:permission>/<int:node_pk>/<int:user_pk>/', ChangeUserPermissions.as_view())

]