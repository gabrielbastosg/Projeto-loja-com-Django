from django.shortcuts import render, get_object_or_404, redirect
from produtos.models import Produto,Categoria
# Create your views here.
def listar_produtos(request):
    produtos = Produto.objects.all() # pega todos os produtos do banco
    return render(request, 'core/lista_produtos.html',{'produtos':produtos})

def produtos_por_categoria(request, categoria_id):
    categoria = get_object_or_404(Categoria, id=categoria_id)
    produtos = Produto.objects.filter(categoria=categoria)

    return render(request, 'core/lista_produtos.html', {
        'produtos': produtos,
        'categoria': categoria
    })

# View de editar produto
def editar_produto(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id)
    if request.method == 'POST':
        produto.nome = request.POST['nome']
        produto.preco = request.POST['preco']
        produto.estoque = request.POST['estoque']
        produto.save()
        return redirect('lista_produtos')
    return render(request, 'core/editar_produto.html', {'produto': produto})

# View de excluir produto
def excluir_produto(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id)
    produto.delete()
    return redirect('lista_produtos')
    