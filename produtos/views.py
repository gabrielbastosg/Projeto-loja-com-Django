from django.shortcuts import render, get_object_or_404, redirect
from .models import Produto, Venda, Categoria
from .forms import VendaForm
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Sum, F, DecimalField, ExpressionWrapper, Value
from django.db.models.functions import Coalesce, TruncDate
from django.utils import timezone
from datetime import timedelta
from django.http import HttpResponse
import csv

# ========================
# Views de Produtos
# ========================

def produto_detalhe(request, id):
    produto = get_object_or_404(Produto, id=id)
    return render(request, 'produtos/detalhe.html', {'produto': produto})

def vender_produto(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id)
    form = VendaForm(request.POST or None)

    if form.is_valid():
        quantidade = form.cleaned_data['quantidade']

        if quantidade > produto.estoque:
            messages.error(request, f'Estoque insuficiente! Só há {produto.estoque} unidade(s) disponível(is).')
        else:
            venda = form.save(commit=False)
            venda.produto = produto
            venda.save()

            produto.estoque -= quantidade
            produto.save()

            messages.success(request, f'Venda de {quantidade} "{produto.nome}" realizada com sucesso!')
            return redirect('lista_produtos')
    
    return render(request, 'produtos/vender.html', {'form': form, 'produto': produto})

def lista_produtos(request):
    busca = request.GET.get('busca', '')
    categoria_slug = request.GET.get('categoria', '')

    produtos = Produto.objects.all()
    if busca:
        produtos = produtos.filter(nome__icontains=busca)
    if categoria_slug:
        produtos = produtos.filter(categoria__slug=categoria_slug)

    categorias = Categoria.objects.all()
    total_produtos = produtos.count()
    total_estoque = sum(p.estoque for p in produtos)

    context = {
        'produtos': produtos,
        'busca': busca,
        'categoria_slug': categoria_slug,
        'categorias': categorias,
        'total_produtos': total_produtos,
        'total_estoque': total_estoque,
    }

    return render(request, 'produtos/lista.html', context)

def repor_produto(request, id):
    produto = get_object_or_404(Produto, id=id)
    produto.estoque += 1
    produto.save()
    return redirect('lista_produtos')

def historico_vendas(request):
    vendas_lista = Venda.objects.select_related('produto').only('id', 'produto', 'quantidade', 'data_venda').order_by('-data_venda')
    paginator = Paginator(vendas_lista, 10)
    page_number = request.GET.get('page')
    vendas = paginator.get_page(page_number)
    return render(request, 'produtos/historico_vendas.html', {'vendas': vendas})

# ========================
# Dashboard
# ========================

def dashboard(request):
    # Pegando o período do GET, padrão 30 dias
    periodo = request.GET.get('periodo', '30')
    hoje = timezone.now().date()

    if periodo == '7':
        data_inicio = hoje - timedelta(days=7)
    elif periodo == '30':
        data_inicio = hoje - timedelta(days=30)
    elif periodo == 'mes':
        data_inicio = hoje.replace(day=1)
    else:
        data_inicio = None

    # Query base de vendas
    vendas_query = Venda.objects.select_related('produto')
    if data_inicio:
        vendas_query = vendas_query.filter(data_venda__date__gte=data_inicio)

    # Métricas de cards
    total_produtos = Produto.objects.count()
    total_estoque = Produto.objects.aggregate(total=Coalesce(Sum('estoque'), 0))['total']
    total_vendas = vendas_query.count()
    total_itens_vendidos = vendas_query.aggregate(total=Coalesce(Sum('quantidade'), 0))['total']
    
    # Faturamento seguro: multiplicando no Python, evitando FieldError
    faturamento = 0
    for venda in vendas_query:
        faturamento += float(venda.quantidade) * float(venda.produto.preco)

    # Vendas por dia para gráfico
    vendas_por_dia = (
        vendas_query
        .values('data_venda')
        .annotate(total=Sum('quantidade'))
        .order_by('data_venda')
    )
    datas = [v['data_venda'].strftime('%d/%m') for v in vendas_por_dia]
    totais = [v['total'] for v in vendas_por_dia]

    # Top 5 produtos do período
    top_produtos = (
        vendas_query
        .values('produto__nome')
        .annotate(total=Sum('quantidade'))
        .order_by('-total')[:5]
    )

    # Preparar cards
    cards = [
        {'classe': 'produtos', 'icone': 'fas fa-box', 'titulo': 'Produtos cadastrados', 'valor': total_produtos},
        {'classe': 'estoque', 'icone': 'fas fa-warehouse', 'titulo': 'Itens em estoque', 'valor': total_estoque},
        {'classe': 'vendas', 'icone': 'fas fa-shopping-cart', 'titulo': 'Total de vendas', 'valor': total_vendas},
        {'classe': 'itens', 'icone': 'fas fa-list', 'titulo': 'Itens vendidos', 'valor': total_itens_vendidos},
        {'classe': 'faturamento', 'icone': 'fas fa-dollar-sign', 'titulo': 'Faturamento total', 'valor': f"{faturamento:.2f}"},
    ]

    context = {
        'cards': cards,
        'datas': datas,
        'totais': totais,
        'top_produtos': top_produtos,
        'periodo': periodo,
    }

    return render(request, 'produtos/dashboard.html', context)

# ========================
# Exportar CSV
# ========================

def exportar_vendas_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="vendas.csv"'

    writer = csv.writer(response)
    writer.writerow(['Data','Produto','Quantidade','Total'])

    vendas = Venda.objects.select_related('produto').all().order_by('-data_venda')

    for v in vendas:
        writer.writerow([
            v.data_venda.strftime('%d/%m/%Y'),
            v.produto.nome,
            v.quantidade,
            v.quantidade * v.produto.preco  # calculando total corretamente
        ])

    return response