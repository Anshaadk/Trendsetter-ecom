from django import forms
from .models import *
from order.models import *
from django.utils.safestring import mark_safe



# class CategoryForm(forms.ModelForm):
#     class Meta:
#          model = Category
#          fields = ['category_name', 'slug','description', 'cat_image',]
        
#     def __init__(self, *args, **kwargs):
#         super(CategoryForm,self).__init__(*args, **kwargs)
#         for field  in self.fields:
#             self.fields[field].widget.attrs['class'] = 'form-control'
# class SubCategoryForm(forms.ModelForm):
#     class Meta:
#          model = Sub_Category
#          fields = ['sub_category_name', 'slug', 'description', 'category', 'is_featured',]
         
        
#     def __init__(self, *args, **kwargs):
#         super(SubCategoryForm,self).__init__(*args, **kwargs)
#         for field  in self.fields:
#             self.fields[field].widget.attrs['class'] = 'form-control'
#             self.fields['is_featured'].widget.attrs['class'] = 'form-check-input small-checkbox'       

    


# class ProductForm(forms.ModelForm):
#     class Meta:
#         model = Product
#         fields = ['product_name', 'slug', 'description', 'price', 'unit', 'image_1', 'image_2', 'image_3', 'image_4', 'stock',
#                   'is_available', 'is_featured', 'category']

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields['price'].widget.attrs['min'] = 0
#         self.fields['stock'].widget.attrs['min'] = 0
#         self.fields['category'].widget.attrs['onchange'] = "getval(this);"
#         self.fields['is_available'].widget.attrs['class'] = 'form-check-input small-checkbox'
#         self.fields['is_featured'].widget.attrs['class'] = 'form-check-input small-checkbox'
        


#         for field_name, field in self.fields.items():
#             classes = field.widget.attrs.get('class', '')
#             classes += ' form-control'
#             field.widget.attrs['class'] = classes.strip()

#         # Add Bootstrap styles to the form labels
#         self.label_suffix = mark_safe('<span class="text-primary">*</span>')
        

            
# class VariationForm(forms.ModelForm):
#     class Meta:
#         model = Variation
#         fields = ['product', 'variation_category', 'variation_value', 'is_active']
#         widgets = {
#             'product': forms.Select(attrs={'class': 'form-control'}),
#             'variation_category': forms.Select(attrs={'class': 'form-control'}),
#             'variation_value': forms.TextInput(attrs={'class': 'form-control'}),
#             'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
#         }
        
#     def __init__(self, *args, **kwargs):
#         super(VariationForm,self).__init__(*args, **kwargs)
#         for field in self.fields:
#             self.fields[field].widget.attrs['class'] = 'form-control'
#         self.fields['is_active'].widget.attrs['class'] = 'form-check-input'

# class CouponForm(forms.ModelForm):
#     class Meta:
#         model = Coupon
#         fields = ['code', 'discount', 'min_value', 'valid_from', 'valid_at', 'active']
#         widgets = {
#             'valid_from': forms.DateTimeInput(attrs={'type': 'datetime-local','placeholder': 'First Name', 'class':'form-control bg-white','style':'max-width:300px;'}),
#             'valid_at': forms.DateTimeInput(attrs={'type': 'datetime-local','placeholder': 'First Name','class':'form-control bg-white', 'style':'max-width:300px;'}),
#             'code': forms.TextInput(attrs={'placeholder': 'Coupon code', 'class': 'form-control bg-white','style':'max-width:300px;'}),
#             'discount': forms.NumberInput(attrs={'placeholder': 'Discount', 'class': 'form-control bg-white','style':'max-width:300px;'}),
#             'min_value': forms.NumberInput(attrs={'placeholder': 'Minimum value', 'class': 'form-control bg-white','style':'max-width:300px;'}),
# }