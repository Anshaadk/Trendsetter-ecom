from django.urls import path,include
from .import views
from django.conf.urls import handler404, handler500, handler403, handler400
from account.views import error_404



urlpatterns = [
    path('',views.home,name='home'),
    path('us_product/',views.us_products,name='us_products'),
    path('cart',views.viewcart, name='cart'),
    path('addtocart/<int:variant_id>/', views.addtocart, name='addtocart'),
    
    # path('sort/<int:pid>/<int:w>/',views.sort, name='sort'),
    path('category/<int:cid>/', views.category, name="category"),
    
    path('removecartproduct/<int:product_id>/', views.removecartproduct,name='removecartproduct'),
    path('addcartitem/<int:product_id>/', views.addcartitem,name='addcartitem'),
    path('removecartitem/<int:product_id>/', views.removecartitem,name='removecartitem'),
    path('removewishlist/<int:product_id>/<int:w>',views.remove_from_wishlist,name='remove_from_wishlist'),
    path('search/',views.search,name='search'),
    path('myaccount/',views.myaccount,name='myaccount'),
    
    path('filterplace/<int:cid>/', views.filterplace, name='filterplace'),
    

    path('<int:id>/', views.product_details, name='product_details'),


    # path('filterplace/', views.filter_by_price, name='filter_products'),
    path('wishlist/', views.userwishlist, name="wishlist"),
    path('addwishlist/<int:product_id>/',views.add_to_wishlist,name='add_to_wishlist'),
    path('removewishlist/<int:product_id>/',views.remove_from_wishlist,name='remove_from_wishlist'),
    path('checkout/',views.checkout, name='checkout'),
    path('orderbook/', views.orderbook, name='orderbook'),
    path('proceed_to_pay/',views.razorPayCheck,name='razorpaycheck'), 
    
 
    
    path('vieworder/<int:id>/',views.viewOrder, name='vieworder'),
    # path('vieworder/<int:id>/',views.viewOrder, name='vieworder'),

]
# handler404 = error_404
