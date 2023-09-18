from django.db import models
from django.urls import reverse




# Create your models here.

COLOR_CHOICES = (
    ('White','White'),
    ('Black','Black'),
    ('Green','Green'),
    ('Red','Red'),
    ('Yellow','Yellow'),
    ('Blue','Blue'),
    ('Brown','Brown'),
    ('Orange','Orange'),
)

SIZE_CHOICES = (
    ('XS','XS'),
    ('S','S'),
    ('M','M'),
    ('L','L'),
    ('XL','XL'),
    ('XXL','XXL'),
    ('XXXL','XXXL'),
    ('7','7'),
    ('8','8'),
    ('9','9'),
    ('10','10'),
    ('11','11'),
    ('12','12'),
    ('28','28'),
    ('30','30'),
    ('32','32'),
    ('34','34'),
    ('36','36'),
    ('38','38'),    
    ('40','40'),
    ('42','42'),
    ('UNI','UNI'),
)

class Category(models.Model):
    name = models.CharField( max_length=50)
    created = models.DateTimeField(auto_now_add=True,null=True)
    is_disable=models.BooleanField(default=False)

    def __str__(self):
        return self.name
    
class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    updated = models.DateField(auto_now=True)
    created = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name
    
class Variant(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    color = models.CharField(choices=COLOR_CHOICES,max_length=10, null= True)
    # name = models.ForeignKey(Color, on_delete=models.CASCADE)
    price = models.PositiveBigIntegerField()
    dprice = models.PositiveBigIntegerField(null=True)
    img1 = models.ImageField(upload_to='uploads')
    img2 = models.ImageField(upload_to='uploads',null=True)
    img3 = models.ImageField(upload_to='uploads',null=True)
    available = models.BooleanField(default=True)
    updated = models.DateField(auto_now=True)
    created = models.DateField(auto_now_add=True)
    

    def __str__(self):
        return f"{self.product} ({self.color})"
    
class Size(models.Model):
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE)
    size = models.CharField(choices=SIZE_CHOICES,max_length=10, null= True)
    stock = models.PositiveIntegerField(null=True)
    available = models.BooleanField(default=True)
    updated = models.DateField(auto_now=True)
    created = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.variant}) ({self.size})"
    
    def __str__(self):
        return self.size
      

   