from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
import requests
from firebase_config import db

from app.models import Categoria, Contato, Produto, Compra
from app.forms import FormCategoria, FormContato, ProdutoForm, FormUsuario
from datetime import datetime

# API / Dados Mockados de Hardware e Eletrônicos utilizados na vitrine externa
PRODUTOS_ELETRONICOS_API = [
    {
        'id': 1,
        'nome': 'Placa de Vídeo RTX 4070 Ti',
        'categoria': 'Componentes / GPUs',
        'preco': '5499.00',
        'estoque': 8,
        'especificacoes': '12GB GDDR6X, Ray Tracing, DLSS 3.0',
        'imagem_emoji': '📟'
    },
    {
        'id': 2,
        'nome': 'Processador Core i7-14700K',
        'categoria': 'Componentes / CPUs',
        'preco': '2899.00',
        'estoque': 14,
        'especificacoes': '20 Cores, 28 Threads, Max Turbo 5.6GHz',
        'imagem_emoji': '🎛️'
    },
    {
        'id': 3,
        'nome': 'Teclado Mecânico RGB Switch Blue',
        'categoria': 'Periféricos',
        'preco': '450.00',
        'estoque': 25,
        'especificacoes': 'Layout ABNT2, Anti-Ghosting, Outemu Blue',
        'imagem_emoji': '⌨️'
    },
    {
        'id': 4,
        'nome': 'Monitor Gamer 27" Quad HD 165Hz',
        'categoria': 'Monitores e Telas',
        'preco': '1999.00',
        'estoque': 5,
        'especificacoes': 'Painel IPS, 1ms de resposta, FreeSync Premium',
        'imagem_emoji': '🖥️'
    }
]

def logar(request):
    formulario = AuthenticationForm(request, data=request.POST or None)
    
    if request.method == 'POST':
        if formulario.is_valid():
            # Faz o login do usuário padrão do Django
            auth_login(request, formulario.get_user())
            
            # Pega o 'next' da URL para fazer o redirecionamento funcionar
            proxima_pagina = request.GET.get('next')
            if proxima_pagina:
                return redirect(proxima_pagina)
                
            return redirect('index')

    return render(request, 'login.html', {'form': formulario})

def index(request):
    avaliacoes = []
    try:
        docs = db.collection('avaliacao').stream()
        for doc in docs:
            dados = doc.to_dict()
            dados['id'] = doc.id
            avaliacoes.append(dados)
    except Exception as e:
        print(f"Erro ao carregar avaliações do Firebase: {e}")
    
    return render(request, 'index.html', {'avaliacoes': avaliacoes})

# Página Quem Somos: Texto descritivo sobre a empresa + Nome dos alunos
def quem_somos(request):
    integrantes = ["Maria do Grau", "Aluno 2", "Aluno 3"]
    return render(request, 'quem-somos.html', {'alunos': integrantes})

# Página Contato: Clientes enviam formulário sem precisar de login
def addContato(request):
    formulario = FormContato(request.POST or None)
    if request.method == 'POST':
        if formulario.is_valid():
            formulario.save()
            messages.success(request, "Mensagem enviada com sucesso!")
            return redirect('addcontato')

    return render(request, 'mensagem.html', {'form': formulario})

def addUsuario(request):
    formulario = FormUsuario(request.POST or None)
    if request.method == 'POST': # Ajustado para o padrão do Django
        if formulario.is_valid():
            usuario = formulario.save()
            
            
            grupo_cliente, created = Group.objects.get_or_create(name="Cliente")
            usuario.groups.add(grupo_cliente)
            
            from django.contrib.auth import login as auth_login
            auth_login(request, usuario)
        
            return redirect('index')

    return render(request, 'cadastro.html', {'form': formulario})

def listarProduto(request):
    _produtos = Produto.objects.all()
    # Enviamos a lista mockada de eletrônicos no lugar da antiga fakestoreapi
    return render(request, 'produto.html', {
        'produtos': _produtos,
        'produtos_api': PRODUTOS_ELETRONICOS_API,
    })

# Processamento de Compras: Atualiza estoque local e registra a venda no perfil
@login_required
def comprar_produto(request, produto_id, tipo):
    if tipo == 'local':
        produto = get_object_or_404(Produto, id=produto_id)
        if produto.estoque > 0:
            produto.estoque -= 1
            produto.save()
            Compra.objects.create(
                usuario=request.user,
                produto_nome=produto.nome,
                preco=produto.preco,
                quantidade=1
            )
            messages.success(request, f"Compra de {produto.nome} finalizada!")
        else:
            messages.error(request, "Desculpe, este produto está esgotado no estoque.")
    
    elif tipo == 'api':
        try:
            # Localiza o eletrônico correspondente pelo ID dentro da API simulada
            prod_api = next((item for item in PRODUTOS_ELETRONICOS_API if item['id'] == int(produto_id)), None)
            
            if prod_api:
                Compra.objects.create(
                    usuario=request.user,
                    produto_nome=prod_api['nome'],
                    preco=float(prod_api['preco']),
                    quantidade=1
                )
                messages.success(request, f"Compra de {prod_api['nome']} finalizada com sucesso!")
            else:
                messages.error(request, "Produto eletrônico não localizado na API.")
        except Exception as e:
            messages.error(request, f"Erro ao processar compra do produto externo: {e}")

    return redirect('perfil')


def perfil(request):
   
    historico_sessao = request.session.get('historico_compras', [])
    
    contexto = {
        
        'compras': historico_sessao,
        'historico': historico_sessao,
    }
    return render(request, 'perfil.html', contexto)

@login_required
def avaliacao(request):
    if request.method == 'POST':
        comentario = request.POST.get('comentario')
        nota = request.POST.get('nota')

        db.collection('avaliacao').add({
            'cliente': request.user.username,
            'comentario': comentario,
            'nota': int(nota)
        })
        messages.success(request, "Obrigado pela sua avaliação!")
        return redirect('index')
    
    return render(request, 'avaliacao.html')


@staff_member_required
def dashboard(request):
    return render(request, 'dashboard.html')

# Controle de Categorias
@staff_member_required
def listarCategoria(request):
    _categorias = Categoria.objects.all().values()
    return render(request, 'categoria.html', {'categorias': _categorias})

@staff_member_required
def addCategoria(request):
    formulario = FormCategoria(request.POST or None)
    if request.method == 'POST':
        if formulario.is_valid():
            formulario.save()
            return redirect('categoria')
    return render(request, 'add-categoria.html', {'form': formulario})

@staff_member_required
def editCategoria(request, id_cat):
    _categoria = get_object_or_404(Categoria, id=id_cat)
    formulario = FormCategoria(request.POST or None, instance=_categoria)
    if request.method == 'POST':
        if formulario.is_valid():
            formulario.save()
            return redirect('categoria')
    return render(request, 'edit-categoria.html', {'form': formulario})

@staff_member_required
def delCategoria(request, id_cat):
    _categoria = get_object_or_404(Categoria, id=id_cat)
    _categoria.delete()
    return redirect('categoria')

# Controle de Mensagens
@staff_member_required
def listarMensagens(request):
    _contatos = Contato.objects.all().values()
    return render(request, 'listar-mensagens.html', {'contatos': _contatos})

@staff_member_required
def delContato(request, id_cont):
    _contato = get_object_or_404(Contato, id=id_cont)
    _contato.delete()
    messages.success(request, "Diretriz de contato arquivada com sucesso.")
    return redirect('listarmensagens')

@staff_member_required
def addProduto(request):
    if request.method == 'POST':
        form = ProdutoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            
            return redirect('listarprodutoadmin') 
    else:
        form = ProdutoForm()
        
    return render(request, 'add-produto.html', {'form': form})
def editproduto(request, id):
    produto = get_object_or_404(Produto, id=id)
    
    if request.method == 'POST':
        
        form = ProdutoForm(request.POST, request.FILES, instance=produto)
        if form.is_valid():
            form.save()
            return redirect('listarprodutoadmin') 
    else:
        form = ProdutoForm(instance=produto)
        
    return render(request, 'add-produto.html', {'form': form, 'editando': True})


def delproduto(request, id):
    produto = get_object_or_404(Produto, id=id)
    produto.delete()
    return redirect('listarprodutoadmin')

@staff_member_required
def delProduto(request, id_prod):
    produto = get_object_or_404(Produto, id=id_prod)
    produto.delete()
    return redirect('produto')

# Controle de Usuários
@staff_member_required
def listarUsuarios(request):
    _usuarios = User.objects.all().values()
    return render(request, 'listar-usuarios.html', {'usuarios': _usuarios})

@staff_member_required
def delUsuario(request, id_user):
    usuario = get_object_or_404(User, id=id_user)
    usuario.delete()
    return redirect('listarusuarios')


@staff_member_required
def listarVendas(request):
    vendas = Compra.objects.all().order_by('-data_compra')
    return render(request, 'listar-vendas.html', {'vendas': vendas})

@staff_member_required
def delVenda(request, id_venda):
    venda = get_object_or_404(Compra, id=id_venda)
    venda.delete()
    return redirect('listarvendas')


@staff_member_required
def listarAvaliacoesAdmin(request):
    avaliacoes = []
    docs = db.collection('avaliacao').stream()
    for doc in docs:
        dados = doc.to_dict()
        dados['id'] = doc.id
        avaliacoes.append(dados)
    return render(request, 'listar-avaliacoes.html', {'avaliacoes': avaliacoes})

@staff_member_required
def delAvaliacao(request, doc_id):
    db.collection('avaliacao').document(doc_id).delete()
    return redirect('listaravaliacoes')

@staff_member_required
def listarProdutoAdmin(request):
    
    _produtos = Produto.objects.all()
    return render(request, 'produto-admin.html', {'produtos': _produtos})

@login_required
def remover_comprador(request, id):
    
    comprador = get_object_or_404(User, id=id)
    comprador.delete()
    
    return redirect('listarusuarios')


@login_required
def editar_comprador(request, id):
    comprador = get_object_or_404(User, id=id)
    
    if request.method == 'POST':
        comprador.username = request.POST.get('username')
        comprador.email = request.POST.get('email')
        comprador.save()
        
        return redirect('listarusuarios')
        
    
    return render(request, 'editar-comprador.html', {'comprador': comprador})


def addContato(request):
    formulario = FormContato(request.POST or None)
    if request.POST:
        if formulario.is_valid():
            formulario.save()
            
            
            messages.success(request, "Diretriz enviada com sucesso! Nossa equipe entrará em contato.")
            
            return redirect('addcontato')
            
    return render(request, 'mensagem.html', {'form': formulario})

@staff_member_required
def admin_add_comprador(request):
   
    formulario = FormUsuario(request.POST or None)
    
    if request.method == 'POST':
        if formulario.is_valid():
            
            novo_comprador = formulario.save()
            
            
            grupo_cliente, created = Group.objects.get_or_create(name="Cliente")
            novo_comprador.groups.add(grupo_cliente)
            
            
            messages.success(request, f"Comprador '{novo_comprador.username}' cadastrado com sucesso no sistema!")
            
           
            return redirect('listarusuarios')

    return render(request, 'admin-add-comprador.html', {'form': formulario})

def adicionar_ao_carrinho(request, produto_id):
   
    produto = get_object_or_404(Produto, id=produto_id)
    
    
    if 'carrinho' not in request.session:
        request.session['carrinho'] = {}
    
    carrinho = request.session['carrinho']
    id_str = str(produto_id)

    
    if id_str in carrinho:
        carrinho[id_str]['quantidade'] += 1
    else:
        carrinho[id_str] = {
            'id': produto.id,
            'nome': produto.nome, # Verifique se no seu model chama-se 'nome' ou 'produto_nome'
            'preco': float(produto.preco),
            'quantidade': 1
        }
    
    
    request.session.modified = True
    messages.success(request, f"{produto.nome} adicionado ao seu terminal de compras!")
    
    # ALTERADO: Mude de 'produto' para 'ver_carrinho'
    return redirect('ver_carrinho')

def ver_carrinho(request):
    # CORRIGIDO: .get('carrinho', {}) usando parênteses corretos
    carrinho = request.session.get('carrinho', {})
    
    total_geral = 0
    total_itens = 0
    produtos_carrinho = []
    
    for item in carrinho.values():
        subtotal = item['preco'] * item['quantidade']
        total_geral += subtotal
        total_itens += item['quantidade']
        
        produtos_carrinho.append({
            'id': item['id'],
            'nome': item['nome'],
            'preco': item['preco'],
            'quantidade': item['quantidade'],
            'subtotal': subtotal
        })
        
    contexto = {
        'carrinho': produtos_carrinho,
        'total_geral': total_geral,
        'total_itens': total_itens
    }
    
    return render(request, 'carrinho.html', contexto)


def limpar_carrinho(request):
    if 'carrinho' in request.session:
        del request.session['carrinho']
    messages.info(request, "Terminal de compras limpo e reiniciado.")
    return redirect('ver_carrinho')

def perfil(request):
    # Recupera o histórico armazenado na sessão (retorna uma lista vazia se não houver compras)
    historico = request.session.get('historico_compras', [])
    
    contexto = {
        # ... mantenha os dados do usuário que você já envia normalmente (nome, email, etc.) ...
        'compras': historico
    }
    return render(request, 'perfil.html', contexto)

def finalizar_compra(request):
    carrinho = request.session.get('carrinho', {})
    
    if not carrinho:
        messages.error(request, "Seu terminal de compras está vazio.")
        return redirect('produto')
    
    if 'historico_compras' not in request.session:
        request.session['historico_compras'] = []
    historico = request.session['historico_compras']
    proximo_pedido_num = len(historico) + 1
    
    for item in carrinho.values():
        nova_compra = {
            'pedido': f"#{proximo_pedido_num}",
            'nome': item['nome'],
            'preco': item['preco'],
            'quantidade': item['quantidade'],
            'data': datetime.now().strftime('%d/%m/%Y %H:%M')
        }
        historico.append(nova_compra)
        proximo_pedido_num += 1
    request.session['historico_compras'] = historico
    
    del request.session['carrinho']
    request.session.modified = True
    
    messages.success(request, "⚡ Ordem de compra processada com sucesso no terminal!")
    
    
    return redirect('perfil')

def comprar_produto(request, produto_id, tipo='local'):
    # 1. Busca o produto no banco pelo ID enviado pelo botão
    produto = get_object_or_404(Produto, id=produto_id)
    
    # 2. Inicia o histórico na sessão caso não exista
    if 'historico_compras' not in request.session:
        request.session['historico_compras'] = []
        
    historico = request.session['historico_compras']
    
    # 3. Define o número do próximo pedido com base no tamanho da lista
    num_pedido = len(historico) + 1
    
    # 4. Cria o dicionário exatamente como a sua tabela do perfil renderiza
    nova_compra = {
        'pedido': f"#{num_pedido}",
        'nome': produto.nome,
        'preco': float(produto.preco),
        'quantidade': 1,
        'data': datetime.now().strftime('%d/%m/%Y %H:%M')
    }
    
    # 5. Adiciona e salva na sessão do navegador
    historico.append(nova_compra)
    request.session['historico_compras'] = historico
    request.session.modified = True
    
    messages.success(request, f"⚡ {produto.nome} adicionado aos seus adquiridos!")
    
    # 6. Redireciona direto para a página do perfil
    return redirect('perfil')