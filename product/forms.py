from django import forms
from .models import CartItems, Product,Category, Size, SubCategory

class ProductForm(forms.ModelForm):
    sizes = forms.ModelMultipleChoiceField(
        queryset=Size.objects.all(),
        widget=forms.CheckboxSelectMultiple,
    )
    class Meta:
        model = Product
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'style': 'width: 500px;', 'class': 'form-control'})
        self.fields['description'].widget.attrs.update({'style': 'width: 500px;', 'class': 'form-control'})
        self.fields['category'].widget.attrs.update({'style': 'width: 500px;', 'class': 'form-control'})
        self.fields['subcategory'].widget.attrs.update({'style': 'width: 500px;', 'class':'form-control'})
        self.fields['price'].widget.attrs.update({'style': 'width: 500px;', 'class': 'form-control'})
        self.fields['offer'].widget.attrs.update({'style':'width:500px;','class':'form-control'})
        self.fields['stock'].widget.attrs.update({'style': 'width: 500px;', 'class': 'form-control'})
        #self.fields['size'].widget.attrs.update({'style':'width:500px;','class':'form-control'})
        self.fields['brand'].widget.attrs.update({'style': 'width: 500px;', 'class': 'form-control'})
        self.fields['image1'].widget.attrs.update({'style': 'width: 500px;', 'class': 'form-control'})
        self.fields['image2'].widget.attrs.update({'style': 'width: 500px;', 'class': 'form-control'})
        self.fields['image3'].widget.attrs.update({'style': 'width: 500px;', 'class': 'form-control'})
        self.fields['image4'].widget.attrs.update({'style': 'width: 500px;', 'class': 'form-control'})

# class CartItemsForm(forms.ModelForm):
#     size = forms.ModelChoiceField(queryset=Size.objects.all())

#     class Meta:
#         model = CartItems
#         fields = ['product', 'quantity', 'size']

#     def _init_(self, *args, **kwargs):
#         super()._init_(*args, **kwargs)

class CartItemsForm(forms.ModelForm):
    size = forms.ModelChoiceField(queryset=Size.objects.none())
    class Meta:
        model = CartItems
        fields = ['size','quantity']

    def __init__(self, *args, **kwargs):
        product = kwargs.pop('product', None)
        super().__init__(*args, **kwargs)
        if product:
            self.fields['size'].queryset = product.sizes.all()
