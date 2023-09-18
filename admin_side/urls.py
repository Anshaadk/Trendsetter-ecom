from django.urls import path,include
from .views import *
from django.conf.urls import handler404, handler500, handler403, handler400
from account.views import error_404



urlpatterns = [
    
    path('admin_panel/',admin_panel,name='admin_panel'),
    path('dashbord/',admindashboard,name='dashbord'),
    path('manage_order/', manage_order, name="manage_order"),
    path('manage_order_con/', manage_order, name="manage_order_con"),
    path('editcategory/<int:category_id>/',editcategory, name='editcategory'),

    path('orderdetails/<int:id>/', orderdetails, name="orderdetails"),
    path('searchorder/', searchorder, name="searchorder"),
    path('update_order/<int:id>/', update_order, name="update_order"),
    path('admincancelOrder/<int:id>/',admincancelOrder, name='admincancelOrder'),

    path('sales/',sales,name='sales'),
    path('list_users/',list_users,name='list_users'),
    path('',admin_login,name='admin_login'),
    path('',admin_logout,name='admin_logout'),
    path('<int:id>/blockuser/', blockuser, name='blockuser'),

    path('viewcategory/', viewcategory, name="viewcategory"),
    path('addcategory/', addcategory, name="addcategory"),
    path('deletecategory/<int:id>/', deletecategory, name="deletecategory"),
    path('enable_category/<int:category_id>/',disable_category, name='disable_category'),
    path('disable_category/<int:category_id>/', enable_category, name='enable_category'),
    path('searchcategory/', searchcategory, name="searchcategory"),
    path('viewproduct/', viewproduct, name="viewproduct"),
    path('searchproduct/', searchproduct, name="searchproduct"),
    path('editproduct/<int:id>/', editproduct, name="editproduct"),
    path('productdetails/<int:id>/', productdetails, name="productdetails"),
    path('addproduct/', addproduct, name="addproduct"),
    path('deleteproduct/<int:id>/', deleteproduct, name="deleteproduct"),
    path('viewvariant/', viewvariant, name="viewvariant"),
    path('searchvariant/', searchvariant, name="searchvariant"),
    path('addvariant/<int:id>/', addvariant, name="addvariant"),
    path('deletevariant/<int:id>/', deletevariant, name="deletevariant"),
    path('addsizeandstock/<int:id>/', addsizeandstock, name="addsizeandstock"),
    path('deletesize/<int:id>/', deletesize, name="deletesize"),
    path('editvariant/<int:id>/', editvariant, name="editvariant"),
    path('view_coupon/',view_coupon,name='view_coupon'),
    path('add_coupons/',add_coupons,name='add_coupons'),
    path('edit_coupon/<int:pid>/',edit_coupon,name='edit_coupon'),
    path('delete_coupon/<int:pid>/',delete_coupon,name='delete_coupon'),
        

    




]
# handler404 = error_404
