from django.db import models
from django.utils.text import slugify

# Create your models here.

class Categoria(models.Model):
    nome = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)  # adiciona o slug

    def save(self, *args, **kwargs):
        # cria automaticamente o slug a partir do nome, se não existir
        if not self.slug:
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome

# ====== PRODUTO =======
class Produto(models.Model):
    nome = models.CharField(max_length=100)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    preco = models.DecimalField(max_digits=8, decimal_places=2)
    estoque = models.IntegerField()

    def __str__(self):
        return self.nome



# ======= VENDA ============
class Venda(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.PROTECT)
    quantidade = models.IntegerField()
    data_venda = models.DateTimeField(auto_now_add=True)  # renomeado

    def __str__(self):
        return f'{self.produto.nome} - {self.quantidade}'

    @property
    def valor_total(self):
        return self.quantidade * self.produto.preco