from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import Permission,Group

# Create your models here.
class Customer(AbstractUser):
    email = models.EmailField(unique=True)
    profile_pic = models.ImageField(upload_to='profile_pics', null=True, blank=True)
    phone = models.CharField(max_length=10, default=1234567890, null=True, blank=True)
    address = models.CharField(max_length=50, null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    state = models.CharField(max_length=50, null=True, blank=True)
    pincode = models.IntegerField(null=True, blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name='customers')
    groups = models.ManyToManyField(Group, related_name='customers')

class UserOTP(models.Model):
    user=models.ForeignKey(Customer,on_delete=models.CASCADE)
    time_st=models.DateTimeField(auto_now=True)
    otp=models.IntegerField()

class AddressDetails(models.Model):
    user = models.ForeignKey(Customer, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=15)
    email = models.EmailField(max_length=50)
    order_address = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=10)
    is_disable=models.BooleanField(default=False)

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def full_address(self):
        return f"{self.order_address},{self.city}, {self.state}, {self.country}, PIN: {self.zip_code}"
    
    def _str_(self):
        return self.user.username
