from django.urls import path
from .views import (NodeView, OrderView, OrderCountView)

urlpatterns = [

	path('node/<int:pk>', NodeView.as_view(), name="tbd"),
	path('orders/', OrderView.as_view(), name="idk"),
	path('counts/', OrderCountView.as_view(), name='nullll')

]