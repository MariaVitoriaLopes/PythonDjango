from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from app.models import Produto
from .serializers import ProdutoSerializer

from django.shortcuts import render

@api_view(['GET'])
def listarProdutosApi(request):
    produtos = Produto.objects.all()
    serializer = ProdutoSerializer(produtos, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def buscarProdutosApi(request, id):
    try:
        produto = Produto.objects.get(id=id)

    except Produto.DoesNotExists:
        return Response({'erro': 'Produto não encontrado'}, status=status.HTTP_404_NOT_FOUND)

    serializer = ProdutoSerializer(produto)

    return Response(serializer.data)

@api_view(['POST'])
def cadastrarProdutoApi(request):
    serializer = ProdutoSerializer(data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data,status=status.HTTP_201_CREATED)

    return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
def atualizarProdutoApi(request, id):
    try:
        produto = Produto.objects.get(id=id)
    except Produto.DoesNotExist:
        return Response({'erro': 'Produto não encontrado'},
        status=status.HTTP_404_NOT_FOUND
        )

    serializer = ProdutoSerializer(produto, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    
    return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def deletarProdutoApi(request, id):
    try:
        produto = Produto.objects.get(id=id)
    except Produto.DoesNotExist:
        return Response({'erro': 'Produto não encontrado'},
        status=status.HTTP_404_NOT_FOUND
        )

    produto.delete()
    
    return Response({'mensagem':'Produto excluido com sucesso'},
                    status=status.HTTP_204_NO_CONTENT)