from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_produtos, name='lista_produtos'),  # lista e filtro
    path('<int:id>/', views.produto_detalhe, name='produto_detalhe'),  # detalhe do produto
    path('<int:produto_id>/vender/', views.vender_produto, name='vender_produto'),  # vender produto
    path('repor/<int:id>/', views.repor_produto, name='repor_produto'),
    path('historico-vendas/', views.historico_vendas, name='historico_vendas'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('exportar-csv/',views.exportar_vendas_csv, name='exportar_csv')
]