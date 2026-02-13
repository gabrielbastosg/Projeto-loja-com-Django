from django import template

register = template.Library()

@register.filter
def brl(value):
    """
    Formata números para moeda brasileira: R$ 1.234,56
    """
    try:
        value = float(value)
    except (ValueError, TypeError):
        return value
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")