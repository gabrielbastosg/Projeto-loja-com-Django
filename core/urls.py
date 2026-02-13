from django.urls import path
from . import views

urlpatterns = [
    path('', views.listar_produtos, name='lista_produtos'),

    path('categoria/<int:categoria_id>/', views.produtos_por_categoria, name='produtos_por_categoria'),
    
    path('editar/<int:produto_id>/', views.editar_produto, name='editar_produto'),
    path('excluir/<int:produto_id>/', views.excluir_produto, name='excluir_produto'),
]