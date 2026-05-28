from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # 1. AUTENTICAÇÃO NO TOPO (Garante que o Django use o seu redirecionamento)
    path("login/", auth_views.LoginView.as_view(template_name="login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page='index'), name="logout"),
    
    # 2. SEUS INCLUDES ABAIXO
    path('', include('app.urls')),
    path('api/', include('api.urls')),

    # 3. ALTERAR SENHA
    path(
        "alterar-senha/",
        auth_views.PasswordChangeView.as_view(
            template_name="alterar-senha.html",
            success_url="confirma"
        ),
        name="alterarsenha"
    ),
    path(
        "alterar-senha/confirma/",
        auth_views.PasswordChangeDoneView.as_view(
            template_name="confirma-senha.html"
        ),
        name="confirmasenha"
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)