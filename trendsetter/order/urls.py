from django.contrib import admin
from django.urls import path,include
from .import views
from django.conf.urls import handler404, handler500, handler403, handler400
# from account.views import error_404

urlpatterns = [
   
   # path('place_order/',views.place_order,name='place_order'),
    path('confirmation/<int:id>/',views.confirmation, name='confirmation'),
    path('placeorder/', views.placeOrder, name='place_order'),
    path('ordercomplete/<str:ordernumber>/',views.orderComplete, name='order_complete'),
    
    
    path('cancelOrder/',views.cancelOrder, name='cancelOrder'),
]
# handler404 = error_404
