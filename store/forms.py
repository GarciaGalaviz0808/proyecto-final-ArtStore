# forms.py - VERSION COMPLETA
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Producto, Artista, EncargoPersonalizado, Categoria, Pedido, ItemPedido

class RegistroForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True, label='Nombre')
    last_name = forms.CharField(max_length=30, required=True, label='Apellido')
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Este correo electrónico ya está registrado.')
        return email

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = '__all__'
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
            'precio': forms.NumberInput(attrs={'step': '0.01'}),
        }

class ArtistaForm(forms.ModelForm):
    class Meta:
        model = Artista
        fields = '__all__'
        widgets = {
            'biografia': forms.Textarea(attrs={'rows': 4}),
        }

class EncargoForm(forms.ModelForm):
    class Meta:
        model = EncargoPersonalizado
        fields = '__all__'
        exclude = ['cliente', 'estado', 'fecha_solicitud', 'fecha_actualizacion']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Describe los detalles de tu obra'}),
            'fecha_entrega_estimada': forms.DateInput(attrs={'type': 'date'}),
            'dimensiones': forms.TextInput(attrs={'placeholder': 'Ej: 40x50 cm'}),
            'presupuesto_maximo': forms.NumberInput(attrs={'step': '0.01'}),
        }

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = '__all__'

class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = '__all__'
        exclude = ['numero_pedido', 'usuario', 'fecha_pedido', 'fecha_actualizacion']
        widgets = {
            'direccion_envio': forms.Textarea(attrs={'rows': 3}),
            'notas': forms.Textarea(attrs={'rows': 2}),
            'subtotal': forms.NumberInput(attrs={'step': '0.01', 'readonly': 'readonly'}),
            'iva': forms.NumberInput(attrs={'step': '0.01', 'readonly': 'readonly'}),
            'total': forms.NumberInput(attrs={'step': '0.01', 'readonly': 'readonly'}),
        }

class AgregarAlCarritoForm(forms.Form):
    cantidad = forms.IntegerField(
        min_value=1, 
        initial=1, 
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'style': 'width: 80px'
        })
    )