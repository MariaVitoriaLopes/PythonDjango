from django import forms
from app.models import Categoria, Contato, Produto
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class FormUsuario(UserCreationForm): 
    class Meta:
        model=User
        fields=['username', 'email', 'password1', 'password2' ]
        labels= {
            'username' : 'Nome',
            'email' : 'E-mail'
        }

class FormEditarUsuario(forms.ModelForm):
    class Meta:
        model=User
        fields=['username', 'email']
        labels={
            'username': 'Nome',
            'email' : 'E-mail'
        }

class FormCategoria(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nome']

class FormContato(forms.ModelForm):
    class Meta:
        model = Contato
        fields = ['nome', 'email', 'mensagem']


class ProdutoForm(forms.ModelForm):
    class Meta:
        model= Produto
        fields=['nome','imagem','estoque','preco','categoria']