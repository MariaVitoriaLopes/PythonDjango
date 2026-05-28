from django.urls import path
from . import views

urlpatterns = [
    
    path('', views.index, name="index"),
    path('quem-somos/', views.quem_somos, name="quem_somos"),
    path('contato/', views.addContato, name='addcontato'),
    
    
    path('categoria/', views.listarCategoria, name='categoria'),
    path('add-categoria/', views.addCategoria, name='addcategoria'),
    path('edit-categoria/<int:id_cat>/', views.editCategoria, name='editcategoria'),
    path('del-categoria/<int:id_cat>/', views.delCategoria, name='delcategoria'),
    
    
    path('ver-mensagens/', views.listarMensagens, name='listarmensagens'),
    path('del-contato/<int:id_cont>/', views.delContato, name='delcontato'),
    
    
    path('produto/', views.listarProduto, name='produto'),
    path('add-produto/', views.addProduto, name='addproduto'),
    path('del-produto/<int:id_prod>/', views.delProduto, name='delproduto'),
    path('comprar/<int:produto_id>/<str:tipo>/', views.comprar_produto, name='comprar_produto'),
    
    
    path('cadastro/', views.addUsuario, name='cadastro'),
    path('listar-usuarios/', views.listarUsuarios, name='listarusuarios'),
    path('del-usuario/<int:id_user>/', views.delUsuario, name='delusuario'),
    
    
    path('perfil/', views.perfil, name='perfil'),
    path('avaliacao/', views.avaliacao, name="avaliacao"),

    path('edit-produto/<int:id>/', views.editproduto, name='editproduto'),
    path('del-produto/<int:id>/', views.delproduto, name='delproduto'),

    path('remover-comprador/<int:id>/', views.remover_comprador, name='remover_comprador'),
    path('editar-comprador/<int:id>/', views.editar_comprador, name='editar_comprador'),
    
    
    path('dashboard/', views.dashboard, name='dashboard'),
    path('vendas/', views.listarVendas, name='listarvendas'),
    path('del-venda/<int:id_venda>/', views.delVenda, name='delvenda'),
    path('admin-avaliacoes/', views.listarAvaliacoesAdmin, name='listaravaliacoes'),
    path('del-avaliacao/<str:doc_id>/', views.delAvaliacao, name='delavaliacao'),
    path('admin-produtos/', views.listarProdutoAdmin, name='listarprodutoadmin'),

    
    path('admin-add-comprador/', views.admin_add_comprador, name='admin_add_comprador'),
    path('carrinho/adicionar/<int:produto_id>/', views.adicionar_ao_carrinho, name='adicionar_ao_carrinho'),
    path('carrinho/', views.ver_carrinho, name='ver_carrinho'),
    path('carrinho/limpar/', views.limpar_carrinho, name='limpar_carrinho'),
    path('carrinho/finalizar/', views.finalizar_compra, name='finalizar_compra'),
]