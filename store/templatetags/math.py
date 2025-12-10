# store/templatetags/math_filters.py
from django import template

register = template.Library()

@register.filter(name='multiply')
def multiply(value, arg):
    """Multiplica el valor por el argumento"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter(name='add_tax')
def add_tax(value, tax_percent=16):
    """Añade impuesto al valor"""
    try:
        value = float(value)
        return value + (value * float(tax_percent) / 100)
    except (ValueError, TypeError):
        return 0

@register.filter(name='calculate_tax')
def calculate_tax(value, tax_percent=16):
    """Calcula solo el impuesto"""
    try:
        return float(value) * float(tax_percent) / 100
    except (ValueError, TypeError):
        return 0