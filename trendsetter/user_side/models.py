from django.db import models
from account.models import *
from admin_side.models import *
from django.core.validators import MinValueValidator,MaxValueValidator
from django.contrib.auth import get_user_model

# Create your models here.


# class CartItem(models.Model):
#     product = models.ForeignKey(ProductVarient, on_delete=models.CASCADE)
#     user = models.ForeignKey(Customer, on_delete=models.CASCADE,null=True)
#     quantity = models.PositiveIntegerField(default=0)
#     size=models.CharField(max_length=10)
#     created_at = models.DateTimeField(auto_now_add=True)
#     is_active = models.BooleanField(default=True)
    
#     def __str__(self):
#         return f"{self.quantity} x {self.product}"
    
#     def sub_total(self):
#         return (self.product.price-(self.product.price*(self.product.offer/100))) * self.quantity


# class City(models.Model):
#     name=models.CharField( max_length=50)
 
 
#     def __str__(self):
#         return self.name
    
# class State(models.Model):
#     name= models.CharField( max_length=50)

#     def __str__(self):
#         return self.name
    

# class Wishlist(models.Model):
#     user = models.OneToOneField(Customer, on_delete=models.CASCADE)

# class WishlistItem(models.Model):
#     wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE)
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)

#     def __str__(self):
#         return f"{self.wishlist.user.username}'s wishlist item: {self.product.name}"




