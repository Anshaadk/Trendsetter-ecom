from django.urls import path,include
from .import views
from django.conf.urls import handler404, handler500, handler403, handler400



urlpatterns = [

    path('login/',views.login,name='login'),
    path('register/',views.register,name='register'),
    path('',views.logout,name='logout'),
    path('forgetpassword/',views.forgetpassword,name='forgetpassword'),
    path('resetpassword_validate/<uidb64>/<token>/', views.resetpassword_validate, name='resetpassword_validate'),
    path('resetpassword/',views.resetpassword,name='resetpassword'),
    path('updateprofile/',views.updateprofile,name='updateprofile'),
    path('add_address/', views.add_address, name='add_address'),
    path('manageaddress/',views.manageaddress,name='manageaddress'),
    path('deleteaddress/<int:id>/',views.deleteaddress,name='deleteaddress'),
    path('enable_address/<int:id>/',views. enable_address, name='enable_address'),
    path('disable_address/<int:id>/', views.disable_address, name='disable_address'),
    path('edit_address/<int:id>/', views.edit_address, name='editaddress'),
    path('change-password/',views. change_password, name='change_password'),
    path('confi_add_address/',views.confi_add_address,name='confi_add_address'),

    


]
# handler404 = views.error_404
