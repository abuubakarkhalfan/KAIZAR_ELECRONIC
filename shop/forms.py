from django import forms
from .models import Product

class CheckoutForm(forms.Form):
    customer_name = forms.CharField(max_length=140, label="Jina kamili")
    phone = forms.CharField(max_length=24, label="Namba ya simu")
    delivery_area = forms.CharField(max_length=240, label="Eneo la kufikishiwa")
    payment_method = forms.ChoiceField(choices=[("M-Pesa", "M-Pesa"), ("Tigo Pesa", "Tigo Pesa"), ("Airtel Money", "Airtel Money"), ("Cash", "Malipo wakati wa kupokea")], label="Njia ya malipo")

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["brand", "name", "description", "price", "image", "is_active"]
        labels = {"brand":"Chapa", "name":"Jina la simu", "description":"Maelezo", "price":"Bei (TZS)", "image":"Picha ya bidhaa", "is_active":"Ionekane dukani"}
        widgets = {"description": forms.Textarea(attrs={"rows": 3})}

    def clean_image(self):
        image = self.cleaned_data.get("image")
        if image:
            if image.size > 5 * 1024 * 1024:
                raise forms.ValidationError("Picha isiwe zaidi ya MB 5.")
            if image.content_type not in ["image/jpeg", "image/png", "image/webp"]:
                raise forms.ValidationError("Tumia JPG, PNG au WebP.")
        return image
